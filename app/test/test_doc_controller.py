import io
import os
import tempfile
import pytest
from uuid import uuid4
from flask import current_app
from app.models.user_model import User
from app.models.doc_model import Document
from app.extensions import db
from app.controllers.doc_controller import (
    save_uploaded_file, list_documents,
    download_document, delete_document
)
from werkzeug.datastructures import FileStorage

def unique_email():
    return f"user_{uuid4().hex}@example.com"


@pytest.fixture
def setup_user(app, db):
    user = User(email=unique_email(), role="editor")
    user.set_password("testpass")
    db.session.add(user)
    db.session.commit()
    return user


def test_save_uploaded_file_success(app, db, setup_user, tmp_path):
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    file = FileStorage(
        stream=io.BytesIO(b"test content"),
        filename="doc.txt",
        content_type="text/plain"
    )

    with app.app_context():
        result, status = save_uploaded_file(file, setup_user.id, "My Doc")
        assert status == 201
        assert result["title"] == "My Doc"

        expected_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{setup_user.id}_doc.txt")
        assert os.path.exists(expected_path)



def test_list_documents(app, db, setup_user, tmp_path):
    with app.app_context():
        doc = Document(title="Doc 1", filename="file.txt", created_by=setup_user.id)
        db.session.add(doc)
        db.session.commit()

        docs, status = list_documents()
        assert status == 200
        assert isinstance(docs, list)
        assert any(d["title"] == "Doc 1" for d in docs)


def test_download_document_success(app, db, setup_user, tmp_path):
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    filename = f"{setup_user.id}_download.txt"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    with open(file_path, "w") as f:
        f.write("test")

    with app.app_context():
        doc = Document(title="Download", filename=filename, created_by=setup_user.id)
        db.session.add(doc)
        db.session.commit()

        response = download_document(doc.id)
        assert response.status_code == 200
        assert response.direct_passthrough is True


def test_download_document_not_found(app, db):
    with app.app_context():
        result, status = download_document(9999)
        assert status == 404
        assert result["msg"] == "Document not found"


def test_delete_document_success(app, db, setup_user, tmp_path):
    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    filename = f"{setup_user.id}_delete.txt"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    with open(file_path, "w") as f:
        f.write("delete me")

    with app.app_context():
        doc = Document(title="To Delete", filename=filename, created_by=setup_user.id)
        db.session.add(doc)
        db.session.commit()

        result, status = delete_document(doc.id, setup_user.id)
        assert status == 200
        assert result["msg"] == "Document deleted"
        assert not os.path.exists(file_path)


def test_delete_document_not_found(app, db, setup_user):
    with app.app_context():
        result, status = delete_document(9999, setup_user.id)
        assert status == 404
        assert result["msg"] == "Document not found"


def test_delete_document_forbidden(app, db, setup_user):
    other_user = User(email=unique_email(), role="editor")
    other_user.set_password("pass")
    db.session.add(other_user)
    db.session.commit()

    with app.app_context():
        doc = Document(title="Unauthorized Delete", filename="test.txt", created_by=other_user.id)
        db.session.add(doc)
        db.session.commit()

        result, status = delete_document(doc.id, setup_user.id)
        assert status == 403
        assert result["msg"] == "Forbidden"
