from flask import Blueprint
from flask_jwt_extended import get_jwt, jwt_required
from app.controllers.ingestion_controller import get_ingestion_list, trigger_ingestion, get_ingestion_status

ingestion_bp = Blueprint("ingestion_bp", __name__)

@ingestion_bp.route("/<int:doc_id>/trigger", methods=["POST"])
@jwt_required()
def trigger(doc_id):
    claims = get_jwt()
    if claims.get("role") not in ["admin", "editor"]:
        return {"msg": "Forbidden"}, 403 
    return trigger_ingestion(doc_id)

@ingestion_bp.route("/<int:ing_id>/status", methods=["GET"])
@jwt_required()
def status(ing_id):
    claims = get_jwt()
    if claims.get("role") not in ["admin", "editor"]:
        return {"msg": "Forbidden"}, 403 
    return get_ingestion_status(ing_id)

@ingestion_bp.route("/", methods=["GET"])
@jwt_required()
def list_ingestions():
    claims = get_jwt()
    if claims.get("role") not in ["admin", "editor"]:
        return {"msg": "Forbidden"}, 403 
    return get_ingestion_list()
