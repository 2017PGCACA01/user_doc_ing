import re
from sqlalchemy.orm import validates
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

VALID_ROLES = {"viewer", "editor", "admin"}
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="viewer", nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @validates("role")
    def validate_role(self, key, value):
        if value not in VALID_ROLES:
            raise ValueError(f"Invalid role '{value}', must be one of {VALID_ROLES}")
        return value

    @validates("email")
    def validate_email(self, key, value):
        if not EMAIL_REGEX.match(value):
            raise ValueError("Invalid email format")
        return value
