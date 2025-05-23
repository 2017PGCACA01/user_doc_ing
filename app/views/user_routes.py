from flask import Blueprint, request
from pydantic import ValidationError

from app.controllers.user_controller import register_user, update_user_role, user_login
from app.models.user_model import User
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, get_jwt_identity

from app.schemas.user_schema import UserRegisterSchema

user_bp = Blueprint("user", __name__)

@user_bp.route("/register", methods=["POST"])
def register():
    try:
        json_data = request.get_json()
        validated_data = UserRegisterSchema(**json_data)
    except ValidationError as e:
        return {"errors": e.errors()}, 400
    return register_user(validated_data.model_dump())


@user_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    token = user_login(data)
    if not token : 
        return {"msg": "Unauthorized"}, 401
    return {"access_token": token}, 200

@user_bp.route("/me", methods=["GET"])
@jwt_required()
def get_profile():
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
    claims = get_jwt()
    if claims.get("role") != "admin":
        return {"msg": "Forbidden: Admins only"}, 403
    data = request.json
    new_role = data.get("role")

    if not new_role:
        return {"msg": "Missing role field"}, 400

    return update_user_role(user_id, new_role)
    