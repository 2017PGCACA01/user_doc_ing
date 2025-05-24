from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models.user_model import User
from sqlalchemy.exc import IntegrityError

def register_user(data):
    """
    Registers a new user with the provided data.
    :param data: Dictionary containing user details (email, password, role)
    :return: A dictionary with a success message or an error message if registration fails.
    :raises: 400 if the email already exists, 500 for other database errors
    """
    user = User(email=data["email"], role=data["role"])
    user.set_password(data["password"])
    db.session.add(user)
    try:
        db.session.commit()
    except  IntegrityError as e:
        db.session.rollback()
        return {"msg": "Duplicate email"}, 400
    except Exception as e:
        db.session.rollback()
        return {"msg": "An error occurred while registering the user"}, 500   
    return {"msg": "User registered successfully"}, 201


def user_login(data):
    """
    Authenticates a user with the provided email and password.
    :param data: Dictionary containing user credentials (email, password)
    :return: Access token if authentication is successful, None otherwise.
    :raises: None if authentication fails, otherwise returns a JWT access token
    """
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return None
    identity = str(user.id)
    additional_claims = {
        "email": user.email,
        "role": user.role
    }
    return create_access_token(identity=identity, additional_claims=additional_claims)

def update_user_role(user_id, new_role):
    """
    Updates the role of a user identified by user_id.
    :param user_id: ID of the user whose role is to be updated
    :param new_role: New role to be assigned to the user
    :return: A dictionary with a success message or an error message if the update fails.
    """
    user = User.query.get(user_id)
    if not user:
        return {"msg": "User not found"}, 404
    try:
        user.role = new_role
        db.session.commit()
    except ValueError:
        db.session.rollback()
        return {"msg": "Role not allowed"}, 400
    except Exception as e:
        db.session.rollback()
        return {"msg": "An error occurred while updating the user role"}, 500
    return {"msg": f"User role updated to {new_role}"}, 200
