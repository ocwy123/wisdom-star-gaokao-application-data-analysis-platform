from app.extensions import db
from datetime import datetime


class SchoolHeat(db.Model):
    __tablename__ = 'ana_school_heat'

    id = db.Column(db.BigInteger, primary_key=True)
    school_id = db.Column(db.BigInteger, db.ForeignKey('edu_school.id'), nullable=False)
    search_count = db.Column(db.Integer, nullable=False)
    favorite_count = db.Column(db.Integer, nullable=False)
    view_count = db.Column(db.Integer, nullable=False)
    heat_score = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    school = db.relationship('School', back_populates='heat_stats')

    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'search_count': self.search_count,
            'favorite_count': self.favorite_count,
            'view_count': self.view_count,
            'heat_score': float(self.heat_score) if self.heat_score else None
        }