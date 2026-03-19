from app.extensions import db
from datetime import datetime


class SchoolMajor(db.Model):
    __tablename__ = 'edu_school_major'

    id = db.Column(db.BigInteger, primary_key=True)
    school_id = db.Column(db.BigInteger, db.ForeignKey('edu_school.id'), nullable=False)
    major_id = db.Column(db.BigInteger, db.ForeignKey('edu_major.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    school = db.relationship('School', back_populates='majors')
    major = db.relationship('Major', back_populates='schools')
