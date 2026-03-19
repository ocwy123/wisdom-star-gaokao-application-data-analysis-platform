from app.extensions import db
from datetime import datetime


class School(db.Model):
    __tablename__ = 'edu_school'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    province = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    is_985 = db.Column(db.Boolean, nullable=False)
    is_211 = db.Column(db.Boolean, nullable=False)
    is_double_first = db.Column(db.Boolean, nullable=False)
    founded_year = db.Column(db.Integer)
    description = db.Column(db.Text)
    website = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    majors = db.relationship('Major', secondary='edu_school_major', back_populates='schools')

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
            'website': self.website
        }