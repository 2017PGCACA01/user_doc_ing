from app.extensions import db
from datetime import datetime

class Ingestion(db.Model):
    __tablename__ = "ingestion"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"), nullable=False)
    status = db.Column(db.String(20), default="queued")
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text, nullable=True)
    summary = db.Column(db.Text, nullable=True)
