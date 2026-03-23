from app.extensions import db
from datetime import datetime


class Favorite(db.Model):
    __tablename__ = 'usr_favorite'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('usr_user.id'), nullable=False)
    favorite_type = db.Column(db.String(50), nullable=False)
    target_id = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user = db.relationship('User', backref='favorites')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'favorite_type': self.favorite_type,
            'target_id': self.target_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }