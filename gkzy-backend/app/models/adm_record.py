from app.extensions import db
from datetime import datetime


class AdmRecord(db.Model):
    __tablename__ = 'edu_adm_record'
    __table_args__ = {'extend_existing': True}   # 添加这一行

    id = db.Column(db.BigInteger, primary_key=True)
    school_id = db.Column(db.BigInteger, db.ForeignKey('edu_school.id'), nullable=False)
    major_name = db.Column(db.String(50), nullable=False)  # 选科类别：物理类、历史类、理科、文科、综合类
    province = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    min_score = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    school = db.relationship('School', back_populates='adm_records')

    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'major_name': self.major_name,
            'province': self.province,
            'year': self.year,
            'min_score': self.min_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
