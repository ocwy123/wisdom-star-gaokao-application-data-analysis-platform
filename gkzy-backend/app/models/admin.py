from app.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Admin(db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    real_name = db.Column(db.String(50))
    role = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'real_name': self.real_name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }