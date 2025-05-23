import os
import io
import tempfile
from flask_jwt_extended import create_access_token
from app.models.user_model import User
from app.models.doc_model import Document
from app.extensions import db
from uuid import uuid4

def unique_email(prefix="user"):
    return f"{prefix}_{uuid4().hex}@example.com"

def test_upload_missing_file_or_title(client, app, db):
    user = User(email=unique_email("upload"), role="editor")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    with app.app_context():
        token = create_access_token(identity=str(user.id))

    # Missing both
    res = client.post("/api/docs/upload", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 400
    assert res.get_json()["msg"] == "Missing file or title"

def test_upload_success(client, app, db):
    user = User(email=unique_email("upload"), role="editor")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    with app.app_context():
        token = create_access_token(identity=str(user.id))

    data = {
        "title": "Test Document",
        "file": (io.BytesIO(b"Sample file content"), "sample.txt")
    }

    res = client.post("/api/docs/upload", headers={
        "Authorization": f"Bearer {token}"
    }, content_type="multipart/form-data", data=data)

    assert res.status_code == 201 or res.status_code == 200

def test_list_documents(client, app, db):
    user = User(email=unique_email("list"), role="editor")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    with app.app_context():
        token = create_access_token(identity=str(user.id))

    res = client.get("/api/docs/", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)

def test_download_document(client, app, db):
    user = User(email=unique_email("download"), role="editor")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    with app.app_context():
        token = create_access_token(identity=str(user.id))

    doc = Document(title="Download Doc", filename="testfile.txt", created_by=user.id)
    db.session.add(doc)
    db.session.commit()

    res = client.get(f"/api/docs/{doc.id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200 or res.status_code == 404

def test_delete_document(client, app, db):
    user = User(email=unique_email("delete"), role="editor")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    with app.app_context():
        token = create_access_token(identity=str(user.id))

    doc = Document(title="Delete Me", filename="delete.txt", created_by=user.id)
    db.session.add(doc)
    db.session.commit()

    res = client.delete(f"/api/docs/{doc.id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200 or res.status_code == 404

def test_upload_no_selected_file(client, app, db):
    user = User(email=unique_email("no_file"), role="editor")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    with app.app_context():
        token = create_access_token(identity=str(user.id))

    data = {
        "title": "No File Test",
        "file": (io.BytesIO(b""), "")  # empty filename triggers the check
    }

    res = client.post("/api/docs/upload", headers={
        "Authorization": f"Bearer {token}"
    }, content_type="multipart/form-data", data=data)

    assert res.status_code == 400
    assert res.get_json()["msg"] == "No selected file"
