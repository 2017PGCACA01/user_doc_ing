import os
from datetime import datetime
from flask import current_app
from app.extensions import db
from app.models.doc_model import Document
from app.models.ingestion_model import Ingestion
import requests

import PyPDF2

def read_pdf(file_path):
    """Reads and returns text from all pages of a PDF file."""
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def process_document_ingestion(app, doc_id):
    """
    Processes the ingestion of a document by its ID.
    This function reads the document content, sends it to a language model for summarization,
    and updates the ingestion status in the database.
    :param app: Flask application instance
    :param doc_id: ID of the document to be ingested
    :return: None
    """
    with app.app_context():
        ingestion = Ingestion.query.filter_by(document_id=doc_id).first()
        doc = Document.query.get(doc_id)

        if not ingestion or not doc:
            return

        ingestion.status = "processing"
        ingestion.started_at = datetime.utcnow()
        db.session.commit()

        try:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], doc.filename)
            if doc.filename.lower().endswith('.pdf'):
                content = read_pdf(file_path)
            else:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            prompt = f"Summarize the following document in about 100 words:\n\n{content}. Do not cross the word limit of 100."
            openrouter_key = "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"
            model_name = "google/gemini-2.5-flash-preview-05-20"
            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": "Bearer " + openrouter_key,
                },
                json={
                    "model":model_name,
                    "stream": False,
                    "options": {"num_predict": 2000},
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            res.raise_for_status()
            summary = res.json()['choices'][0]['message']['content']
            ingestion.status = "done"
            ingestion.completed_at = datetime.utcnow()
            ingestion.summary = str(summary)

        except Exception as e:
            ingestion.status = "failed"
            ingestion.completed_at = datetime.utcnow()
            ingestion.error_message = str(e)
        db.session.commit()
