from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models.user_model import User
from sqlalchemy.exc import IntegrityError

def register_user(data):
    user = User(email=data["email"])
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
