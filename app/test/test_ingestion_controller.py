import pytest
from unittest.mock import patch, MagicMock
from app.models.user_model import User
from app.models.doc_model import Document
from app.models.ingestion_model import Ingestion
from app.controllers.ingestion_controller import (
    trigger_ingestion,
    get_ingestion_status,
    get_ingestion_list
)
from app.extensions import db
from uuid import uuid4


def unique_email():
    return f"user_{uuid4().hex}@example.com"


@pytest.fixture
def test_user(app, db):
    user = User(email=unique_email(), role="editor")
    user.set_password("securepass")
    db.session.add(user)
    db.session.commit()
    return user


def test_trigger_ingestion_success(app, db, test_user):
    with app.app_context():
        doc = Document(title="Trigger Me", filename="dummy.txt", created_by=test_user.id)
        db.session.add(doc)
        db.session.commit()

        with patch("app.controllers.ingestion_controller.process_document_ingestion") as mock_proc:
            response, status = trigger_ingestion(doc.id)
            assert status == 202
            assert response["msg"] == "Ingestion started"
            assert response["document_id"] == doc.id
            mock_proc.assert_called_once()


def test_trigger_ingestion_already_exists(app, db, test_user):
    with app.app_context():
        doc = Document(title="Already Triggered", filename="file.txt", created_by=test_user.id)
        db.session.add(doc)
        db.session.commit()

        ingestion = Ingestion(document_id=doc.id, status="queued")
        db.session.add(ingestion)
        db.session.commit()

        response, status = trigger_ingestion(doc.id)
        assert status == 400
        assert response["msg"] == "Ingestion already exists for this document"


def test_trigger_ingestion_doc_not_found(app, db):
    with app.app_context():
        response, status = trigger_ingestion(9999)
        assert status == 404
        assert response["msg"] == "Document not found"


def test_get_ingestion_status_success(app, db, test_user):
    with app.app_context():
        doc = Document(title="Get Status", filename="test.txt", created_by=test_user.id)
        db.session.add(doc)
        db.session.commit()

        ingestion = Ingestion(document_id=doc.id, status="done", summary="All good")
        db.session.add(ingestion)
        db.session.commit()

        data, status = get_ingestion_status(ingestion.id)
        assert status == 200
        assert data["status"] == "done"
        assert data["summary"] == "All good"


def test_get_ingestion_status_not_found(app, db):
    with app.app_context():
        data, status = get_ingestion_status(9999)
        assert status == 404
        assert data["msg"] == "No ingestion record found"


def test_get_ingestion_list(app, db, test_user):
    with app.app_context():
        doc = Document(title="List Doc", filename="x.txt", created_by=test_user.id)
        db.session.add(doc)
        db.session.commit()

        ingestion = Ingestion(document_id=doc.id, status="processing")
        db.session.add(ingestion)
        db.session.commit()

        result, status = get_ingestion_list()
        assert status == 200
        assert isinstance(result, list)
        assert any(i["document_id"] == doc.id for i in result)

def test_trigger_ingestion_db_failure(app, db, test_user):
    with app.app_context():
        doc = Document(title="Fails DB", filename="fail.txt", created_by=test_user.id)
        db.session.add(doc)
        db.session.commit()

        # Mock commit to raise exception
        with patch("app.controllers.ingestion_controller.db.session.commit", side_effect=Exception("DB commit failed")):
            response, status = trigger_ingestion(doc.id)

        assert status == 500
        assert response["msg"] == "Failed to start ingestion"
