import os
from app.extensions import db
from app.models.doc_model import Document
from app.models.ingestion_model import Ingestion
from flask import current_app, send_from_directory

def save_uploaded_file(file, user_id, title):
    filename = f"{user_id}_{file.filename}"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    doc = Document(title=title, filename=filename, created_by=user_id)
    db.session.add(doc)
    db.session.commit()
    return doc.to_dict(), 201

def list_documents():
    docs = Document.query.all()
    return [doc.to_dict() for doc in docs], 200

def download_document(doc_id):
    doc = Document.query.get(doc_id)
    if not doc:
        return {"msg": "Document not found"}, 404
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'], doc.filename, as_attachment=True
    )

def delete_document(doc_id, user_id):
    doc = Document.query.get(doc_id)
    if not doc:
        return {"msg": "Document not found"}, 404
    if doc.created_by != user_id:
        return {"msg": "Forbidden"}, 403

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    Ingestion.query.filter_by(document_id=doc.id).delete()

    db.session.delete(doc)
    db.session.commit()
    return {"msg": "Document deleted"}, 200
