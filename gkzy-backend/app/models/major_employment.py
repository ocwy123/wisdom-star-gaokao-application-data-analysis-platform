from app.extensions import db
from datetime import datetime


class MajorEmployment(db.Model):
    __tablename__ = 'ana_major_employment'
    __table_args__ = {'extend_existing': True}   # 添加这一行

    id = db.Column(db.BigInteger, primary_key=True)
    major_id = db.Column(db.BigInteger, db.ForeignKey('edu_major.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    avg_salary = db.Column(db.Integer)
    industry_distribution = db.Column(db.Text)
    post_distribution = db.Column(db.Text)
    region_distribution = db.Column(db.Text)
    prospect = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    major = db.relationship('Major')

    def to_dict(self):
        return {
            'id': self.id,
            'major_id': self.major_id,
            'year': self.year,
            'avg_salary': self.avg_salary,
            'industry_distribution': self.industry_distribution,
            'post_distribution': self.post_distribution,
            'region_distribution': self.region_distribution,
            'prospect': self.prospect
        }
