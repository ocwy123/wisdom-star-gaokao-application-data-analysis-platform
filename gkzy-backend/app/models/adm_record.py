from app.extensions import db
from datetime import datetime


class AdmRecord(db.Model):
    __tablename__ = 'edu_adm_record'

    id = db.Column(db.BigInteger, primary_key=True)
    school_id = db.Column(db.BigInteger, db.ForeignKey('edu_school.id'), nullable=False)
    major_id = db.Column(db.BigInteger, db.ForeignKey('edu_major.id'), nullable=False)
    province = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    plan_count = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    batch = db.Column(db.String(50), nullable=False)
    major_group = db.Column(db.String(20), nullable=False)
    min_score = db.Column(db.Integer, nullable=False)
    min_rank = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    school = db.relationship('School', back_populates='adm_records')
    major = db.relationship('Major', back_populates='adm_records')

    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'major_id': self.major_id,
            'province': self.province,
            'year': self.year,
            'plan_count': self.plan_count,
            'subject': self.subject,
            'batch': self.batch,
            'major_group': self.major_group,
            'min_score': self.min_score,
            'min_rank': self.min_rank
        }
