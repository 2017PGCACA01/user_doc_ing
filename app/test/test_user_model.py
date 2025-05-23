import pytest

from app.models.user_model import User
from app.test.conftest import db

def test_user_email_validation_failure(app):
    with app.app_context():
        with pytest.raises(ValueError, match="Invalid email format"):
            user = User(email="invalid-email", role="viewer")
            user.set_password("pass")
            db.session.add(user)