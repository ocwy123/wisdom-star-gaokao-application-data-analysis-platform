from app.extensions import db
from datetime import datetime


class ETLLog(db.Model):
    __tablename__ = 'sys_etl_log'

    id = db.Column(db.BigInteger, primary_key=True)
    job_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Enum('success', 'failed', 'running'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    end_time = db.Column(db.DateTime)
    records_processed = db.Column(db.Integer)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'job_name': self.job_name,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'records_processed': self.records_processed,
            'error_message': self.error_message
        }