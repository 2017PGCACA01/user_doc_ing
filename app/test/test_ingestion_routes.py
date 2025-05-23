import pytest
from flask_jwt_extended import create_access_token
from uuid import uuid4
from app.models.user_model import User
from app.models.doc_model import Document
from app.models.ingestion_model import Ingestion
from app.extensions import db


def unique_email(prefix="user"):
    return f"{prefix}_{uuid4().hex}@example.com"


def create_token(user, app, role="editor"):
    with app.app_context():
        return create_access_token(identity=str(user.id), additional_claims={"role": role})


@pytest.fixture
def editor_user(db):
    user = User(email=unique_email("editor"), role="editor")
    user.set_password("pass")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def viewer_user(db):
    user = User(email=unique_email("viewer"), role="viewer")
    user.set_password("pass")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_document(db, editor_user):
    doc = Document(title="Sample Doc", filename="sample.txt", created_by=editor_user.id)
    db.session.add(doc)
    db.session.commit()
    return doc


@pytest.fixture
def sample_ingestion(db, sample_document):
    ingestion = Ingestion(document_id=sample_document.id, status="queued")
    db.session.add(ingestion)
    db.session.commit()
    return ingestion

def test_trigger_ingestion_authorized(client, app, editor_user, sample_document):
    token = create_token(editor_user, app)
    res = client.post(f"/api/ingestion/{sample_document.id}/trigger", headers={
        "Authorization": f"Bearer {token}"
    })
    assert res.status_code in [200, 202]


def test_trigger_ingestion_forbidden(client, app, viewer_user, sample_document):
    token = create_token(viewer_user, app, role="viewer")
    res = client.post(f"/api/ingestion/{sample_document.id}/trigger", headers={
        "Authorization": f"Bearer {token}"
    })
    assert res.status_code == 403
    assert res.get_json()["msg"] == "Forbidden"


def test_get_ingestion_status_authorized(client, app, editor_user, sample_ingestion):
    token = create_token(editor_user, app)
    res = client.get(f"/api/ingestion/{sample_ingestion.id}/status", headers={
        "Authorization": f"Bearer {token}"
    })
    assert res.status_code == 200
    assert "status" in res.get_json()


def unique_email(prefix="user"):
    return f"{prefix}_{uuid4().hex}@example.com"

def test_get_ingestion_status_forbidden(client, app, db):
    # Setup viewer user
    viewer = User(email=unique_email("viewer"), role="viewer")
    viewer.set_password("viewerpass")
    db.session.add(viewer)

    # Setup dummy ingestion for a doc
    document = Document(title="Test Doc", filename="test.txt", created_by=1)
    db.session.add(document)
    db.session.commit()

    ingestion = Ingestion(document_id=document.id, status="queued")
    db.session.add(ingestion)
    db.session.commit()

    with app.app_context():
        token = create_access_token(identity=str(viewer.id), additional_claims={"role": "viewer"})

    res = client.get(f"/api/ingestion/{ingestion.id}/status", headers={
        "Authorization": f"Bearer {token}"
    })

    assert res.status_code == 403
    assert res.get_json()["msg"] == "Forbidden"


def test_list_ingestions_authorized(client, app, editor_user):
    token = create_token(editor_user, app)
    res = client.get("/api/ingestion/", headers={
        "Authorization": f"Bearer {token}"
    })
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def unique_email(prefix="user"):
    return f"{prefix}_{uuid4().hex}@example.com"

def test_list_ingestions_forbidden(client, app, db):
    viewer = User(email=unique_email("viewer"), role="viewer")
    viewer.set_password("pass123")
    db.session.add(viewer)
    db.session.commit()

    with app.app_context():
        token = create_access_token(identity=str(viewer.id), additional_claims={"role": "viewer"})

    res = client.get("/api/ingestion/", headers={
        "Authorization": f"Bearer {token}"
    })

    # Step 4: Assert 403 forbidden
    assert res.status_code == 403
    assert res.get_json()["msg"] == "Forbidden"
