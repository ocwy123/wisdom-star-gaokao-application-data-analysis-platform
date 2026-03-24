from app.extensions import db
from datetime import datetime


class School(db.Model):
    __tablename__ = 'edu_school'
    __table_args__ = {'extend_existing': True}   # 添加这一行

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, comment='高校名称')
    code = db.Column(db.String(50), nullable=False, comment='学校代码')
    province = db.Column(db.String(20), nullable=False, comment='所在省份')
    city = db.Column(db.String(20), nullable=False, comment='所在城市')
    type = db.Column(db.String(20), nullable=False, comment='院校类型')
    is_985 = db.Column(db.Boolean, nullable=False, default=False, comment='是否985')
    is_211 = db.Column(db.Boolean, nullable=False, default=False, comment='是否211')
    is_double_first = db.Column(db.Boolean, nullable=False, default=False, comment='是否双一流')
    founded_year = db.Column(db.Integer, nullable=True, comment='建校时间')
    description = db.Column(db.Text, nullable=True, comment='学校简介')
    website = db.Column(db.String(255), nullable=True, comment='官网')
    logo = db.Column(db.String(255), nullable=True, comment='校徽URL')
    phd_count = db.Column(db.Integer, nullable=True, comment='博士点数量')
    master_count = db.Column(db.Integer, nullable=True, comment='硕士点数量')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    majors = db.relationship('Major', secondary='edu_school_major', back_populates='schools')
    adm_records = db.relationship('AdmRecord', back_populates='school')
    heat_stats = db.relationship('SchoolHeat', back_populates='school')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'province': self.province,
            'city': self.city,
            'type': self.type,
            'is_985': self.is_985,
            'is_211': self.is_211,
            'is_double_first': self.is_double_first,
            'founded_year': self.founded_year,
            'description': self.description,
            'website': self.website,
            'logo': self.logo,
            'phd_count': self.phd_count,
            'master_count': self.master_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }