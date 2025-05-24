from app.extensions import db
from datetime import datetime

class Ingestion(db.Model):
    """
    Represents an ingestion process for a document.
    This model tracks the status of the ingestion, timestamps for when it started and completed,
    any error messages, and a summary of the document after ingestion.
    Attributes:
        id (int): Unique identifier for the ingestion.
        document_id (int): ID of the document being ingested.
        status (str): Current status of the ingestion (e.g., queued, processing, done, failed).
        started_at (datetime): Timestamp when the ingestion started.
        completed_at (datetime): Timestamp when the ingestion completed.
        error_message (str): Error message if the ingestion failed.
        summary (str): Summary of the document after successful ingestion.
    """
    __tablename__ = "ingestion"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"), nullable=False)
    status = db.Column(db.String(20), default="queued")
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text, nullable=True)
    summary = db.Column(db.Text, nullable=True)
