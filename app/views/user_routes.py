from flask import Blueprint, request
from pydantic import ValidationError

from app.controllers.user_controller import register_user, update_user_role, user_login
from app.models.user_model import User
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, get_jwt_identity

from app.schemas.user_schema import UserRegisterSchema

user_bp = Blueprint("user", __name__)

@user_bp.route("/register", methods=["POST"])
def register():
    """
    This route handles user registration.
    It expects a JSON payload with user details such as email and password.
    If the payload is valid, it registers the user and returns a success message.
    If the payload is invalid, it returns a 400 Bad Request with validation errors.
    If the user already exists, it returns a 400.
    It does not require authentication.
    The user role defaults to "user" upon registration.
    The password is hashed before storing it in the database.
    """
    try:
        json_data = request.get_json()
        validated_data = UserRegisterSchema(**json_data)
    except ValidationError as e:
        return {"errors": e.errors()}, 400
    return register_user(validated_data.model_dump())


@user_bp.route("/login", methods=["POST"])
def login():
    """
    This route handles user login.
    It expects a JSON payload with email and password.
    If the credentials are valid, it returns an access token.
    If the credentials are invalid, it returns a 401 Unauthorized response.
    It does not require authentication.
    """
    data = request.json
    token = user_login(data)
    if not token : 
        return {"msg": "Unauthorized"}, 401
    return {"access_token": token}, 200

@user_bp.route("/me", methods=["GET"])
@jwt_required()
def get_profile():
    """
    This route retrieves the profile of the currently authenticated user.
    It requires a valid JWT token for authentication.
    If the user is found, it returns the user's ID, email, and role.
    If the user is not found, it returns a 404 Not Found response.
    """
    user_data = get_jwt_identity()
    user = User.query.get(int(user_data))
    if not user:
        return {"msg": "User not found"}, 404
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role
    }


@user_bp.route("/<int:user_id>/", methods=["PATCH"])
@jwt_required()
def change_user_role(user_id):
    """
    This route allows an admin user to change the role of another user.
    It requires a valid JWT token for authentication.
    Only users with the "admin" role can access this route.
    It expects a JSON payload with the new role.
    If the user is not found, it returns a 404 Not Found response.
    If the role is successfully updated, it returns a success message.
    """
    claims = get_jwt()
    if claims.get("role") != "admin":
        return {"msg": "Forbidden: Admins only"}, 403
    data = request.json
    new_role = data.get("role")

    if not new_role:
        return {"msg": "Missing role field"}, 400

    return update_user_role(user_id, new_role)

@user_bp.route("/", methods=["GET"])
@jwt_required()
def list():
    """
    This route retrieves a list of all users.
    It requires a valid JWT token for authentication.
    If the request is successful, it returns a list of users with their IDs, emails, and roles.
    """
    users = User.query.all()
    user_list = [{"id": user.id, "email": user.email, "role": user.role} for user in users]
    return {"users": user_list}, 200