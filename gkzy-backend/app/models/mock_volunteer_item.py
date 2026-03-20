from app.extensions import db
from datetime import datetime


class MockVolunteerItem(db.Model):
    __tablename__ = 'usr_mock_volunteer_item'

    id = db.Column(db.BigInteger, primary_key=True)
    volunteer_id = db.Column(db.BigInteger, db.ForeignKey('usr_mock_volunteer.id'), nullable=False)
    school_id = db.Column(db.BigInteger, db.ForeignKey('edu_school.id'), nullable=False)
    major_id = db.Column(db.BigInteger, db.ForeignKey('edu_major.id'), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    probability = db.Column(db.Numeric(5, 2))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    volunteer = db.relationship('MockVolunteer', back_populates='items')
    school = db.relationship('School')
    major = db.relationship('Major')

    def to_dict(self):
        return {
            'id': self.id,
            'volunteer_id': self.volunteer_id,
            'school_id': self.school_id,
            'major_id': self.major_id,
            'priority': self.priority,
            'probability': float(self.probability) if self.probability else None
        }