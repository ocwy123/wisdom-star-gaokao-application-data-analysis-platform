from app.extensions import db
from datetime import datetime

class SchoolMajor(db.Model):
    __tablename__ = 'edu_school_major'
    __table_args__ = {'extend_existing': True}   # 添加这一行

    id = db.Column(db.BigInteger, primary_key=True)
    school_id = db.Column(db.BigInteger, db.ForeignKey('edu_school.id'), nullable=False)
    major_id = db.Column(db.BigInteger, db.ForeignKey('edu_major.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # 关系定义（使用 viewonly=True 避免冲突）
    school = db.relationship('School', back_populates='school_majors', viewonly=True)
    major = db.relationship('Major', back_populates='school_majors', viewonly=True)

    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'major_id': self.major_id,
            'description': self.description
        }