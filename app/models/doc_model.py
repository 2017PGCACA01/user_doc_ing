from app.extensions import db
from datetime import datetime

class Document(db.Model):
    """
    Represents a document in the system.
    This model stores metadata about the document, including its title,
    filename, creation date, and the user who created it.
    Attributes:
        id (int): Unique identifier for the document.
        title (str): Title of the document.
        filename (str): Name of the file associated with the document.
        created_at (datetime): Timestamp when the document was created.
        created_by (int): ID of the user who created the document.
    """
    __tablename__ = "document"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "filename": self.filename,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
        }
