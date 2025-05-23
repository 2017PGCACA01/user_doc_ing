from unittest.mock import patch
import pytest
from flask_jwt_extended import create_access_token
from app.models.user_model import User
from app.extensions import db
from uuid import uuid4


def unique_email(prefix="user"):
    return f"{prefix}_{uuid4().hex}@example.com"

def register_user(client, email, password, role):
    return client.post("/api/users/register", json={
        "email": email,
        "password": password,
        "role": role
    })


def login_user(client, email, password):
    return client.post("/api/users/login", json={
        "email": email,
        "password": password
    })



def test_register_valid_user(client):
    email = unique_email()
    res = client.post("/api/users/register", json={
        "email": email,
        "password": "securepass",
        "role": "viewer"
    })
    assert res.status_code == 201



def test_register_invalid_email(client):
    res = register_user(client, "bad-email", "securepass", "viewer")
    assert res.status_code == 400
    assert "errors" in res.get_json()


def test_register_short_password(client):
    res = register_user(client, "test2@example.com", "short", "editor")
    assert res.status_code == 400
    assert "errors" in res.get_json()


def test_register_invalid_role(client):
    res = register_user(client, "test3@example.com", "securepass", "invalidrole")
    assert res.status_code == 400
    assert "errors" in res.get_json()


def test_login_valid_user(client):
    email = "login@example.com"
    password = "securepass"
    register_user(client, email, password, "viewer")
    res = login_user(client, email, password)
    assert res.status_code == 200
    assert "access_token" in res.get_json()


def test_login_invalid_user(client):
    with patch("app.views.user_routes.user_login", return_value=None):
        res = client.post("/api/users/login", json={
            "email": "fake@example.com",
            "password": "wrong"
        })
        assert res.status_code == 401
        assert res.get_json()["msg"] == "Unauthorized"


def test_get_profile_authorized(client, app, db):
    # Step 1: Create user
    user = User(email="me@example.com", role="viewer")
    user.set_password("securepass")
    db.session.add(user)
    db.session.commit()

    # Step 2: Generate token inside app context
    with app.app_context():
        token = create_access_token(identity=str(user.id))

    # Step 3: Use valid Authorization header
    res = client.get("/api/users/me", headers={
        "Authorization": f"Bearer {token}"
    })

    assert res.status_code == 200
    assert res.get_json()["email"] == "me@example.com"



def test_get_profile_unauthorized(client):
    res = client.get("/api/users/me")
    assert res.status_code == 401


def test_change_user_role_as_admin(client, app, db):
    admin = User(email="admin@example.com", role="admin")
    admin.set_password("adminpass") 
    user = User(email="target@example.com", role="viewer")
    user.set_password("targetpass") 
    db.session.add_all([admin, user])
    db.session.commit()

    with app.app_context():
        token = create_access_token(identity=str(admin.id), additional_claims={"role": "admin"})

    res = client.patch(f"/api/users/{user.id}/", json={"role": "editor"}, headers={
        "Authorization": f"Bearer {token}"
    })

    assert res.status_code == 200
    updated = User.query.get(user.id)
    assert updated.role == "editor"



def test_change_user_role_as_non_admin(client, app, db):
    user1 = User(email="user1@example.com", role="viewer")
    user2 = User(email="user2@example.com", role="viewer")
    user1.set_password("pass1")
    user2.set_password("pass2")
    db.session.add_all([user1, user2])
    db.session.commit()

    with app.app_context():
        token = create_access_token(identity=str(user1.id), additional_claims={"role": "viewer"})

    res = client.patch(f"/api/users/{user2.id}/", json={"role": "admin"}, headers={
        "Authorization": f"Bearer {token}"
    })

    assert res.status_code == 403

def test_get_profile_user_not_found(client, app, db):
    with app.app_context():
        token = create_access_token(identity="9999")

    res = client.get("/api/users/me", headers={
        "Authorization": f"Bearer {token}"
    })

    assert res.status_code == 404
    assert res.get_json()["msg"] == "User not found"


def test_change_user_role_missing_role_field(client, app, db):
    # Setup admin and target user
    admin = User(email=unique_email("admin"), role="admin")
    admin.set_password("adminpass")
    target = User(email=unique_email("user"), role="viewer")
    target.set_password("userpass")
    db.session.add_all([admin, target])
    db.session.commit()

    # Generate JWT token for admin
    with app.app_context():
        token = create_access_token(identity=str(admin.id), additional_claims={"role": "admin"})

    # Send PATCH without 'role' in payload
    res = client.patch(f"/api/users/{target.id}/", json={}, headers={
        "Authorization": f"Bearer {token}"
    })

    # Validate response
    assert res.status_code == 400
    assert res.get_json()["msg"] == "Missing role field"


