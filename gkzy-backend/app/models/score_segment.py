from app.extensions import db
from datetime import datetime


class ScoreSegment(db.Model):
    __tablename__ = 'ana_score_segment'

    id = db.Column(db.BigInteger, primary_key=True)
    province = db.Column(db.String(20), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(20), nullable=False)
    batch = db.Column(db.String(50))
    score = db.Column(db.Integer, nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    same_score_count = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'province': self.province,
            'year': self.year,
            'subject': self.subject,
            'batch': self.batch,
            'score': self.score,
            'rank': self.rank,
            'same_score_count': self.same_score_count
        }