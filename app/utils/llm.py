import os
from datetime import datetime
from flask import current_app
from app.extensions import db
from app.models.doc_model import Document
from app.models.ingestion_model import Ingestion
import requests

def process_document_ingestion(app, doc_id):
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
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()


            prompt = f"Summarize the following document in about 100 words:\n\n{content}. Do not cross the word limit of 100."
            print(prompt)
            res = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "qwen2.5:0.5b",
                    "stream": False,
                    "options": {"num_predict": 2000},
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            print(res)
            res.raise_for_status()
            summary = res.json()["message"]["content"]
            ingestion.status = "done"
            ingestion.completed_at = datetime.utcnow()
            ingestion.summary = str(summary)

        except Exception as e:
            ingestion.status = "failed"
            ingestion.completed_at = datetime.utcnow()
            ingestion.error_message = str(e)
        db.session.commit()
