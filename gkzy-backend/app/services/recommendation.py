import os
import pickle
from datetime import datetime
import numpy as np
import pandas as pd
from app.extensions import db
from app.models.school import School
from app.models.adm_record import AdmRecord
from sqlalchemy import func

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'recommendation_model.pkl')


class RecommendationService:
    model = None
    feature_encoder = None

    @staticmethod
    def _build_history_features(user_province=None, user_subject=None):
        # 按省份+专业维度计算
        query = db.session.query(
            AdmRecord.school_id,
            func.avg(AdmRecord.min_score).label('school_avg_score'),
            func.stddev(AdmRecord.min_score).label('school_std_score')
        ).filter(AdmRecord.year >= 2021)

        if user_province:
            query = query.filter(AdmRecord.province == user_province)
        if user_subject:
            query = query.filter(AdmRecord.major_name == user_subject)

        recs = query.group_by(AdmRecord.school_id).all()

        df = pd.DataFrame([{
            'school_id': r.school_id,
            'school_avg_score': float(r.school_avg_score or 0),
            'school_std_score': float(r.school_std_score or 0)
        } for r in recs])

        if df.empty:
            return pd.DataFrame(columns=['school_id', 'school_avg_score', 'school_std_score'])
        return df

    @classmethod
    def _prepare_training_data(cls):
        # 将每条录取记录转换为训练样本（生成正/负样本）
        records = db.session.query(AdmRecord).filter(AdmRecord.year >= 2021).all()
        if not records:
            return None, None

        history_df = cls._build_history_features()

        samples = []
        np.random.seed(42)  # 确保结果可重现

        # 微调梯度分布参数，稍微放松冲刺区
        gradients = [
            (1, 0.5, 3),   # 1. 压线区：录取分+0.5~+1.5分，3个样本
            (4, 1.2, 4),   # 2. 边缘区：录取分+1.5~+5.5分，4个样本
            (9, 2.5, 5),   # 3. 稳妥区：录取分+4~+14分，5个样本
            (16, 4, 4),    # 4. 安全区：录取分+8~+24分，4个样本
            (28, 6, 2)     # 5. 超安全区：录取分+16~+40分，2个样本
        ]

        for rec in records:
            for mu, sigma, count in gradients:
                for _ in range(count):
                    # 生成符合正态分布的随机偏移量，确保最小偏移为0
                    offset = max(0, int(np.random.normal(mu, sigma)))

                    # 正样本：分数高于录取分的考生
                    positive_score = rec.min_score + offset
                    # 根据分差计算样本权重，分差越大权重越高，但控制在合理范围内
                    weight = max(1, min(4, offset // 2 + 1))  # 权重范围1-4，稍微放宽
                    samples.append({
                        'user_score': positive_score,
                        'user_province': rec.province,
                        'user_subject': rec.major_name,
                        'year': rec.year,
                        'school_id': rec.school_id,
                        'label': 1,
                        'weight': weight  # 添加样本权重
                    })

                    # 负样本：分数明显低于录取分的考生
                    neg_offset = max(3, int(np.random.normal(mu + 4, sigma + 1.5)))
                    negative_score = max(0, rec.min_score - neg_offset)
                    samples.append({
                        'user_score': negative_score,
                        'user_province': rec.province,
                        'user_subject': rec.major_name,
                        'year': rec.year,
                        'school_id': rec.school_id,
                        'label': 0,
                        'weight': 1  # 负样本权重为1
                    })

        df = pd.DataFrame(samples)

        school_info_list = []
        schools = School.query.all()
        for s in schools:
            school_info_list.append({
                'school_id': s.id,
                'school_province': s.province,
                'school_type': s.type,
                'is_985': 1 if s.is_985 else 0,
                'is_211': 1 if s.is_211 else 0,
                'is_double_first': 1 if s.is_double_first else 0
            })
        school_info = pd.DataFrame(school_info_list)

        df = df.merge(school_info, on='school_id', how='left')
        df = df.merge(history_df, on='school_id', how='left')

        # 缺失填充
        df['school_avg_score'] = df['school_avg_score'].fillna(df['user_score'])
        df['school_std_score'] = df['school_std_score'].fillna(0.0)

        # 编码类别特征
        cols_to_encode = ['user_province', 'user_subject', 'school_province', 'school_type']
        cls.feature_encoder = {}
        for c in cols_to_encode:
            df[c] = df[c].astype(str).fillna('UNKNOWN')
            df[c], mapping = pd.factorize(df[c])
            cls.feature_encoder[c] = mapping

        feature_cols = [
            'user_score', 'year',
            'user_province', 'user_subject',
            'school_province', 'school_type',
            'is_985', 'is_211', 'is_double_first',
            'school_avg_score', 'school_std_score'
        ]

        X = df[feature_cols]
        y = df['label']
        # 返回样本权重
        weights = df.get('weight', pd.Series([1] * len(df)))
        return X, y, weights

    @classmethod
    def train_model(cls, force=False):
        if cls.model and not force:
            return cls.model

        if os.path.exists(MODEL_PATH) and not force:
            try:
                with open(MODEL_PATH, 'rb') as f:
                    cls.model = pickle.load(f)
                # 确保feature_encoder也被加载
                encoder_path = MODEL_PATH.replace('.pkl', '_encoder.pkl')
                if os.path.exists(encoder_path):
                    with open(encoder_path, 'rb') as f:
                        cls.feature_encoder = pickle.load(f)
                return cls.model
            except Exception:
                pass

        X, y, weights = cls._prepare_training_data()
        if X is None or y is None or X.empty:
            raise RuntimeError('没有足够的数据进行训练')

        try:
            from lightgbm import LGBMClassifier
            # 微调参数，稍微增加复杂度以更好地捕捉概率差异
            cls.model = LGBMClassifier(
                n_estimators=170,        # 稍微增加树的数量
                learning_rate=0.09,     # 稍微降低学习率
                max_depth=7,            # 稍微增加树深度
                min_child_samples=25,   # 稍微减少叶子节点最小样本数
                subsample=0.8,          # 保持子采样
                colsample_bytree=0.8,   # 保持特征子采样
                reg_alpha=0.9,          # 稍微减少L1正则化
                reg_lambda=0.9,         # 稍微减少L2正则化
                random_state=42,
                verbose=1               # 显示训练进度
            )
            print('Recommendation 模型训练开始：使用 LightGBM，权重样本激活。')
            # 使用样本权重进行训练
            cls.model.fit(X, y, sample_weight=weights)
            print('Recommendation 模型训练完成。')
        except ImportError:
            from sklearn.tree import DecisionTreeClassifier
            cls.model = DecisionTreeClassifier(max_depth=6, random_state=42)
            print('Recommendation 模型训练开始：使用 DecisionTree。')
            cls.model.fit(X, y)
            print('Recommendation 模型训练完成。')

        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(cls.model, f)

        # 保存feature_encoder
        encoder_path = MODEL_PATH.replace('.pkl', '_encoder.pkl')
        with open(encoder_path, 'wb') as f:
            pickle.dump(cls.feature_encoder, f)

        return cls.model

    @classmethod
    def _encode_features(cls, df):
        for c, mapping in cls.feature_encoder.items():
            df[c] = df[c].astype(str).fillna('UNKNOWN')
            df[c] = df[c].apply(lambda x: mapping.get_loc(x) if x in mapping else -1)
        return df

    @classmethod
    def get_volunteer_recommendations(cls, user_score, user_province, user_subject, school_province=None, school_type=None):
        cls.train_model()

        # 首先尝试精确匹配
        query = db.session.query(
            AdmRecord.school_id,
            func.avg(AdmRecord.min_score).label('avg_score')
        ).filter(
            AdmRecord.province == user_province,
            AdmRecord.major_name == user_subject,
            AdmRecord.year >= 2020
        ).group_by(AdmRecord.school_id)

        school_ids = [r.school_id for r in query.all()]

        schools_query = School.query.filter(School.id.in_(school_ids))
        if school_province:
            schools_query = schools_query.filter(School.province == school_province)
        if school_type:
            schools_query = schools_query.filter(School.type == school_type)

        schools = schools_query.all()
        if not schools:
            return {'rush': [], 'stable': [], 'safe': []}

        # 先按照用户省份+选科做统计，再按全量作fallback
        history_df = cls._build_history_features(user_province, user_subject)
        history_df_fallback = cls._build_history_features()

        candidates = []
        for school in schools:
            h = history_df[history_df['school_id'] == school.id]
            if h.empty:
                h = history_df_fallback[history_df_fallback['school_id'] == school.id]

            school_avg_score = float(h['school_avg_score'].iloc[0]) if not h.empty else user_score
            # 筛除过于低于用户分数的学校
            if school_avg_score < user_score - 50:
                continue

            row = {
                'school_id': school.id,
                'user_score': user_score,
                'user_province': user_province,
                'user_subject': user_subject,
                'year': datetime.now().year,
                'school_province': school.province,
                'school_type': school.type,
                'is_985': 1 if school.is_985 else 0,
                'is_211': 1 if school.is_211 else 0,
                'is_double_first': 1 if school.is_double_first else 0,
                'school_avg_score': school_avg_score,
                'school_std_score': float(h['school_std_score'].iloc[0]) if not h.empty else 0.0
            }
            candidates.append(row)

        feature_df = pd.DataFrame(candidates)
        feature_df = cls._encode_features(feature_df)

        # 确保特征列顺序与训练时完全一致
        feature_cols = [
            'user_score', 'year',
            'user_province', 'user_subject',
            'school_province', 'school_type',
            'is_985', 'is_211', 'is_double_first',
            'school_avg_score', 'school_std_score'
        ]

        proba = cls.model.predict_proba(feature_df[feature_cols])
        # 如果二分类，取概率为类别1
        predicted = proba[:, 1] if proba.shape[1] > 1 else proba[:, 0]

        rush = []
        stable = []
        safe = []

        for idx, row in feature_df.iterrows():
            school_id = int(row['school_id'])
            probability = float(predicted[idx])
            school = next((s for s in schools if s.id == school_id), None)
            if not school:
                continue

            entry = {
                'id': school.id,
                'name': school.name,
                'province': school.province,
                'city': school.city,
                'type': school.type,
                'is_985': school.is_985,
                'is_211': school.is_211,
                'is_double_first': school.is_double_first,
                'probability': round(probability, 4),
                'avg_score': float(feature_df.loc[idx, 'school_avg_score']),
                'description': school.description,
                'website': school.website,
                'logo': school.logo
            }

            # 微调阈值，稍微降低让推荐更合理
            if probability >= 0.45 and probability < 0.65:
                rush.append(entry)
            elif probability >= 0.65 and probability < 0.85:
                stable.append(entry)
            elif probability >= 0.85:
                safe.append(entry)

        rush.sort(key=lambda x: x['probability'])
        stable.sort(key=lambda x: x['probability'])
        safe.sort(key=lambda x: x['probability'])

        return {
            'rush': rush,
            'stable': stable,
            'safe': safe
        }
