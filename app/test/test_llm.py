import os
import tempfile
import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock
from app.extensions import db
from app.models.user_model import User
from app.models.doc_model import Document
from app.models.ingestion_model import Ingestion
from PyPDF2 import PdfWriter
from app.controllers.ingestion_controller import process_document_ingestion


def generate_unique_email():
    return f"user_{uuid4().hex}@example.com"

def create_user_doc_ingestion(app, db, upload_folder):
    with app.app_context():
        user = User(email=generate_unique_email(), role="editor")
        user.set_password("secret")
        db.session.add(user)
        db.session.commit()

        fd, filepath = tempfile.mkstemp(dir=upload_folder, suffix=".txt")
        os.write(fd, b"This is a test document for ingestion.")
        os.close(fd)

        filename = os.path.basename(filepath)

        doc = Document(title="TestDoc", filename=filename, created_by=user.id)
        db.session.add(doc)
        db.session.commit()

        ingestion = Ingestion(document_id=doc.id, status="queued")
        db.session.add(ingestion)
        db.session.commit()

        return doc.id, filepath


def test_ingestion_skipped_if_missing(app, db):
    """Should skip processing if ingestion/doc does not exist"""
    with app.app_context():
        process_document_ingestion(app, doc_id=9999)  # No doc/ingestion
        # Should not raise error


@patch("requests.post")
def test_ingestion_success(mock_post, app, db, tmp_path):
    """Should mark ingestion as done and save summary"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {"message": {"content": "mocked summary"}}
        ]
    }
    mock_response.raise_for_status = lambda: None
    mock_post.return_value = mock_response

    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    doc_id, _ = create_user_doc_ingestion(app, db, tmp_path)

    process_document_ingestion(app, doc_id)

    with app.app_context():
        ing = Ingestion.query.filter_by(document_id=doc_id).first()
        assert ing.status == "done"
        assert ing.summary == "mocked summary"
        assert ing.completed_at is not None


@patch("requests.post")
def test_ingestion_fails_on_request_error(mock_post, app, db, tmp_path):
    """Should mark ingestion as failed if OpenRouter call fails"""
    mock_post.side_effect = Exception("mock failure")

    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    doc_id, _ = create_user_doc_ingestion(app, db, tmp_path)

    process_document_ingestion(app, doc_id)

    with app.app_context():
        ing = Ingestion.query.filter_by(document_id=doc_id).first()
        assert ing.status == "failed"
        assert "mock failure" in ing.error_message


def test_ingestion_file_not_found(app, db, tmp_path):
    """Should fail if the file is missing from upload folder"""
    with app.app_context():
        user = User(email=generate_unique_email(), role="editor")
        user.set_password("pass")
        db.session.add(user)
        db.session.commit()

        doc = Document(title="MissingFile", filename="not_found.txt", created_by=user.id)
        db.session.add(doc)
        db.session.commit()
        doc_id = doc.id

        ingestion = Ingestion(document_id=doc_id, status="queued")
        db.session.add(ingestion)
        db.session.commit()

    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    process_document_ingestion(app, doc_id)

    with app.app_context():
        ing = Ingestion.query.filter_by(document_id=doc_id).first()
        assert ing.status == "failed"
        assert (
            "No such file" in ing.error_message
            or "No such file or directory" in ing.error_message
        )

@patch("requests.post")
def test_ingestion_with_real_pdf(mock_post, app, db, tmp_path):
    mock_response = MagicMock()
    mock_response.json.return_value = {"choices": [{"message": {"content": "pdf summary"}}]}
    mock_response.raise_for_status = lambda: None
    mock_post.return_value = mock_response

    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    # Create PDF file
    pdf_path = tmp_path / "sample_test.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with open(pdf_path, "wb") as f:
        writer.write(f)

    # Now insert doc and ingestion manually
    with app.app_context():
        user = User(email=generate_unique_email(), role="editor")
        user.set_password("secret")
        db.session.add(user)
        db.session.commit()

        doc = Document(title="PDFTest", filename="sample_test.pdf", created_by=user.id)
        db.session.add(doc)
        db.session.commit()

        ingestion = Ingestion(document_id=doc.id, status="queued")
        db.session.add(ingestion)
        db.session.commit()
        doc_id = doc.id

    # Run ingestion
    process_document_ingestion(app, doc_id)

    # Verify ingestion state
    with app.app_context():
        ing = Ingestion.query.filter_by(document_id=doc_id).first()
        assert ing.status == "done"
        assert ing.summary == "pdf summary"

