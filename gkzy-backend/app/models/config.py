from app.extensions import db
from datetime import datetime


class Config(db.Model):
    __tablename__ = 'sys_config'

    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), nullable=False, unique=True)
    config_value = db.Column(db.Text, nullable=False)
    config_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    updated_by = db.Column(db.Integer, db.ForeignKey('admins.id'))
    updated_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.config_value,
            'config_type': self.config_type,
            'description': self.description,
            'updated_by': self.updated_by
        }