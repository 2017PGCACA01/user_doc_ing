
from unittest.mock import patch
import pytest
from app.extensions import db
from app.models.user_model import User
from app.controllers.user_controller import (
    register_user, user_login, update_user_role
)
from sqlalchemy.exc import IntegrityError 
from flask_jwt_extended import decode_token
from uuid import uuid4


def unique_email():
    return f"user_{uuid4().hex}@example.com"


def test_register_user_success(app, db):
    with app.app_context():
        email = unique_email()
        data = {"email": email, "password": "securepass"}
        res, status = register_user(data)
        assert status == 201
        assert res["msg"] == "User registered successfully"
        assert User.query.filter_by(email=email).first()


def test_register_user_unexpected_error(app, db, monkeypatch):
    with app.app_context():
        data = {"email": unique_email(), "password": "securepass"}
        monkeypatch.setattr(db.session, "commit", lambda: (_ for _ in ()).throw(Exception("DB down")))
        res, status = register_user(data)
        assert status == 500
        assert "An error occurred" in res["msg"]


def test_user_login_success(app, db):
    with app.app_context():
        email = unique_email()
        password = "securepass"
        user = User(email=email, role="editor")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        token = user_login({"email": email, "password": password})
        assert token is not None
        decoded = decode_token(token)
        assert decoded["sub"] == str(user.id)
        assert decoded["email"] == email
        assert decoded["role"] == "editor"


def test_user_login_invalid_password(app, db):
    with app.app_context():
        email = unique_email()
        user = User(email=email, role="viewer")
        user.set_password("correctpass")
        db.session.add(user)
        db.session.commit()

        token = user_login({"email": email, "password": "wrongpass"})
        assert token is None


def test_user_login_nonexistent_user(app):
    token = user_login({"email": unique_email(), "password": "any"})
    assert token is None


def test_update_user_role_success(app, db):
    with app.app_context():
        user = User(email=unique_email(), role="viewer")
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()

        res, status = update_user_role(user.id, "admin")
        assert status == 200
        assert res["msg"] == "User role updated to admin"
        assert User.query.get(user.id).role == "admin"


def test_update_user_role_not_found(app):
    res, status = update_user_role(9999, "admin")
    assert status == 404
    assert res["msg"] == "User not found"


def test_update_user_role_invalid(app, db):
    with app.app_context():
        user = User(email=unique_email(), role="viewer")
        user.set_password("abc")
        db.session.add(user)
        db.session.commit()

        res, status = update_user_role(user.id, "invalid_role")
        assert status == 400
        assert res["msg"] == "Role not allowed"


def test_update_user_role_generic_exception(app, db):
    with app.app_context():
        user = User(email="editor@example.com", role="editor")
        user.set_password("securepass")
        db.session.add(user)
        db.session.commit()

        with patch("app.controllers.user_controller.db.session.commit", side_effect=Exception("commit failed")):
            res, status = update_user_role(user.id, "admin")

        assert status == 500
        assert res["msg"].startswith("An error occurred")


def test_register_user_duplicate_email_mocked(app):
    with app.app_context():
        data = {"email": "duplicate@example.com", "password": "pass123"}
        mock_err = IntegrityError("statement", "params", "orig")

        with patch("app.controllers.user_controller.db.session.commit", side_effect=mock_err):
            res, status = register_user(data)

        assert status == 400
        assert res["msg"] == "Duplicate email"
