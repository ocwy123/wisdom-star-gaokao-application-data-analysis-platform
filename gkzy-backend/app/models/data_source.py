from app.extensions import db
from datetime import datetime


class DataSource(db.Model):
    __tablename__ = 'sys_data_source'
    __table_args__ = {'extend_existing': True}   # 添加这一行

    id = db.Column(db.BigInteger, primary_key=True)
    source_name = db.Column(db.String(200), nullable=False)
    source_type = db.Column(db.String(50), nullable=False)
    api_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'source_name': self.source_name,
            'source_type': self.source_type,
            'api_url': self.api_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
