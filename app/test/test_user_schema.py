import pytest
from pydantic import ValidationError
from app.schemas.user_schema import (
    UserRegisterSchema,
    UserLoginSchema,
    UserResponseSchema
)


def test_register_schema_valid():
    data = {
        "email": "user@example.com",
        "password": "securepass",
        "role": "viewer"
    }
    schema = UserRegisterSchema(**data)
    assert schema.email == "user@example.com"
    assert schema.role == "viewer"

def test_register_schema_invalid_email():
    with pytest.raises(ValidationError) as e:
        UserRegisterSchema(
            email="not-an-email",
            password="securepass",
            role="admin"
        )
    assert "email" in str(e.value)

def test_register_schema_short_password():
    with pytest.raises(ValidationError) as e:
        UserRegisterSchema(
            email="test@example.com",
            password="short",
            role="editor"
        )
    message = str(e.value)
    assert message.startswith("1 validation error for UserRegisterSchema")

def test_register_schema_invalid_role():
    with pytest.raises(ValidationError) as e:
        UserRegisterSchema(
            email="test@example.com",
            password="securepass",
            role="superuser"  # invalid role
        )
    message = str(e.value)
    assert message.startswith("1 validation error for UserRegisterSchema")



def test_login_schema_valid():
    schema = UserLoginSchema(email="test@example.com", password="abc12345")
    assert schema.email == "test@example.com"

def test_login_schema_invalid_email():
    with pytest.raises(ValidationError):
        UserLoginSchema(email="invalid@", password="12345678")

def test_response_schema_valid():
    schema = UserResponseSchema(id=1, email="test@example.com", role="admin")
    assert schema.id == 1
    assert schema.role == "admin"

def test_response_schema_invalid_role():
    with pytest.raises(ValidationError):
        UserResponseSchema(id=1, email="test@example.com", role="owner")
