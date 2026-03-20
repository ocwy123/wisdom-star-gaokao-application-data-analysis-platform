from app.extensions import db
from datetime import datetime


class Major(db.Model):
    __tablename__ = 'edu_major'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    degree = db.Column(db.String(50))
    subjects = db.Column(db.Text)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    schools = db.relationship('School', secondary='edu_school_major', back_populates='majors')
    adm_records = db.relationship('AdmRecord', back_populates='major')
    employment_stats = db.relationship('MajorEmployment', back_populates='major')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'duration': self.duration,
            'degree': self.degree,
            'subjects': self.subjects,
            'description': self.description
        }
