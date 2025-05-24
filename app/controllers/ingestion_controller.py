import os
import threading

from flask import current_app
from app.models.ingestion_model import Ingestion
from app.models.doc_model import Document
from app.extensions import db
from app.utils.llm import process_document_ingestion

def trigger_ingestion(doc_id):
    """
    Triggers the ingestion process for a document by its ID.
    This function checks if the document exists, ensures that an ingestion
    does not already exist for the document, and starts the ingestion process
    in a separate thread.
    :param doc_id: ID of the document to be ingested
    :return: A dictionary with the status of the ingestion process and the document ID,
             or an error message if the ingestion could not be started.
    :raises: 404 if the document is not found, 400 if an ingestion already exists,
    """
    doc = Document.query.get(doc_id)
    if not doc:
        return {"msg": "Document not found"}, 404
    existing = Ingestion.query.filter_by(document_id=doc_id).first()
    if existing:
        return {"msg": "Ingestion already exists for this document"}, 400

    ingestion = Ingestion(document_id=doc_id, status="queued")
    db.session.add(ingestion)
    try:
        db.session.commit()
        threading.Thread(
            target=process_document_ingestion,
            args=(current_app._get_current_object(), doc_id),
            daemon=True
        ).start()
        return {"msg": "Ingestion started", "document_id": doc_id}, 202
    except:
        db.session.rollback()
        return {"msg": "Failed to start ingestion"}, 500
    
def get_ingestion_status(ing_id):
    """
    Retrieves the status of an ingestion by its ID.
    :param ing_id: ID of the ingestion to check
    :return: A dictionary with the ingestion status details,
             or an error message if the ingestion is not found.
    :raises: 404 if the ingestion is not found
    """
    ingestion = Ingestion.query.filter_by(id=ing_id).first()
    if not ingestion:
        return {"msg": "No ingestion record found"}, 404
    return ingestion_status_dict(ingestion), 200

def get_ingestion_list():
    """
    Retrieves a list of all ingestions.
    :return: A list of dictionaries containing the status of each ingestion,
             or an empty list if no ingestions exist.
    """
    ingestions = Ingestion.query.all()
    return [ingestion_status_dict(ing) for ing in ingestions], 200

def ingestion_status_dict(ing):
    """
    Converts an Ingestion object to a dictionary representation.
    :param ing: An Ingestion object
    :return: A dictionary with the ingestion details, including ID, document ID,
             status, timestamps, error message, and summary.
    """
    return {
        "id": ing.id,
        "document_id": ing.document_id,
        "status": ing.status,
        "started_at": ing.started_at.isoformat() if ing.started_at else None,
        "completed_at": ing.completed_at.isoformat() if ing.completed_at else None,
        "error_message": ing.error_message,
        "summary": ing.summary if ing.summary else None
    }
