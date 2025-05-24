from flask import Blueprint, request
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
from app.controllers.doc_controller import (
    save_uploaded_file, list_documents, download_document, delete_document
)

doc_bp = Blueprint("doc", __name__)

@doc_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_document():
    """
    This route allows users to upload documents.
    Only users with 'admin' or 'editor' roles can upload documents.
    It requires a file and a title in the form data.
    The uploaded file is saved, and the document is created in the database.
    If the user does not have the required role, a 403 Forbidden response is returned.
    If the file or title is missing, a 400 Bad Request response is returned.
    If the file is successfully uploaded, a 201 Created response is returned with the document details.
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get("role") not in ["admin", "editor"]:
        return {"msg": "Forbidden"}, 403 
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
    """
    This route allows users to list all documents.
    It requires a valid JWT token for authentication.
    The documents are returned in a paginated format.
    If the user is not authenticated, a 401 Unauthorized response is returned.
    If the request is successful, a 200 OK response is returned with the list of documents.
    """

    return list_documents()

@doc_bp.route("/<int:doc_id>", methods=["GET"])
@jwt_required()
def get_doc(doc_id):
    """
    This route allows users to download a document by its ID.
    It requires a valid JWT token for authentication.
    If the document is found, it is returned with a 200 OK response.
    If the document does not exist, a 404 Not Found response is returned.
    """
    return download_document(doc_id)

@doc_bp.route("/<int:doc_id>", methods=["DELETE"])
@jwt_required()
def delete_doc(doc_id):
    """
    This route allows users to delete a document by its ID.
    It requires a valid JWT token for authentication.
    The user must be the creator of the document to delete it.
    If the document does not exist, a 404 Not Found response is returned.
    """
    user_id = int(get_jwt_identity())
    return delete_document(doc_id, user_id)
