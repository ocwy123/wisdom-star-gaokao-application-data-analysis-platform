from app.extensions import db
from datetime import datetime


class MockVolunteer(db.Model):
    __tablename__ = 'usr_mock_volunteer'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('usr_user.id'), nullable=False)
    is_saved = db.Column(db.Boolean, nullable=False, default=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    user = db.relationship('User')
    items = db.relationship('MockVolunteerItem', back_populates='volunteer', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'is_saved': self.is_saved,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }