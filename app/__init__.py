from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import db, migrate, jwt
from app.views.user_routes import user_bp
from app.views.doc_routes import doc_bp
from app.views.ingestion_routes import ingestion_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(
        app,
        origins=["http://localhost:4200"],
        supports_credentials=False,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"]
    )
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(doc_bp, url_prefix="/api/docs")
    app.register_blueprint(ingestion_bp, url_prefix="/api/ingestion")


    return app
