from flask import Blueprint, request
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
from app.controllers.doc_controller import (
    save_uploaded_file, list_documents, download_document, delete_document
)

doc_bp = Blueprint("doc", __name__)

@doc_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_document():
    user_id = int(get_jwt_identity())
    # claims = get_jwt()
    # if claims.get("role") not in ["admin", "editor"]:
    #     return {"msg": "Forbidden"}, 403 
    if "file" not in request.files or not request.form.get("title"):
        return {"msg": "Missing file or title"}, 400

    file = request.files["file"]
    title = request.form["title"]

    if file.filename == "":
        return {"msg": "No selected file"}, 400

    return save_uploaded_file(file, user_id, title)

@doc_bp.route("/", methods=["GET"])
@jwt_required()
def list_docs():
    return list_documents()

@doc_bp.route("/<int:doc_id>", methods=["GET"])
@jwt_required()
def get_doc(doc_id):
    return download_document(doc_id)

@doc_bp.route("/<int:doc_id>", methods=["DELETE"])
@jwt_required()
def delete_doc(doc_id):
    user_id = int(get_jwt_identity())
    return delete_document(doc_id, user_id)
