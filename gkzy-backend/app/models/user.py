from app.extensions import db
from datetime import datetime
class User(db.Model):
    __tablename__ = 'usr_user'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(100), nullable=False)   # 新增字段
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    role = db.Column(db.String(50), nullable=False, default='普通用户')
    register_time = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'phone': self.phone,
            'email': self.email,
            'role': self.role,
            'register_time': self.register_time.isoformat() if self.register_time else None,
            'status': self.status
        }

