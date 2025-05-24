from flask import Blueprint
from flask_jwt_extended import get_jwt, jwt_required
from app.controllers.ingestion_controller import get_ingestion_list, trigger_ingestion, get_ingestion_status

ingestion_bp = Blueprint("ingestion_bp", __name__)

@ingestion_bp.route("/<int:doc_id>/trigger", methods=["POST"])
@jwt_required()
def trigger(doc_id):
    """
    This route triggers the ingestion process for a document by its ID.
    It requires a valid JWT token for authentication.
    Only users with 'admin' or 'editor' roles can trigger ingestions.
    If the user does not have the required role, a 403 Forbidden response is returned.
    If the ingestion is successfully triggered, a 200 OK response is returned.
    """
    claims = get_jwt()
    if claims.get("role") not in ["admin", "editor"]:
        return {"msg": "Forbidden"}, 403 
    return trigger_ingestion(doc_id)

@ingestion_bp.route("/<int:ing_id>/status", methods=["GET"])
@jwt_required()
def status(ing_id):
    """
    This route retrieves the status of an ingestion by its ID.
    It requires a valid JWT token for authentication.
    Only users with 'admin' or 'editor' roles can access ingestion statuses.
    If the user does not have the required role, a 403 Forbidden response is returned.
    If the ingestion status is successfully retrieved, a 200 OK response is returned with the status details.
    """
    claims = get_jwt()
    if claims.get("role") not in ["admin", "editor"]:
        return {"msg": "Forbidden"}, 403 
    return get_ingestion_status(ing_id)

@ingestion_bp.route("/", methods=["GET"])
@jwt_required()
def list_ingestions():
    """
    This route retrieves a list of all ingestions.
    It requires a valid JWT token for authentication.
    Only users with 'admin' or 'editor' roles can access the ingestion list.
    If the user does not have the required role, a 403 Forbidden response is returned.
    If the ingestion list is successfully retrieved, a 200 OK response is returned with the list of ingestions.
    """
    claims = get_jwt()
    if claims.get("role") not in ["admin", "editor"]:
        return {"msg": "Forbidden"}, 403 
    return get_ingestion_list()
