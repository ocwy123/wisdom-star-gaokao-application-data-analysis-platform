from app.extensions import db
from datetime import datetime


class ConfigLog(db.Model):
    __tablename__ = 'sys_config_log'

    id = db.Column(db.BigInteger, primary_key=True)
    admin_id = db.Column(db.BigInteger, db.ForeignKey('admins.id'))
    action = db.Column(db.String(50), nullable=False)
    config_key = db.Column(db.String(100), nullable=False)
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'action': self.action,
            'config_key': self.config_key,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'ip_address': self.ip_address
        }