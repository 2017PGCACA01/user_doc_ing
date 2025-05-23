# Flask Document Management System (DMS)

This is a fully tested, modular Flask-based Document Management System with JWT authentication, role-based access, ingestion pipeline, and test coverage. It supports file upload, document ingestion via an LLM, and secure access patterns.

---

## Features

- ✅ JWT-based user authentication
- ✅ Role-based access control (`viewer`, `editor`, `admin`)
- ✅ Upload, list, download, and delete documents
- ✅ Trigger asynchronous ingestion via LLM summarization
- ✅ PostgreSQL backend
- ✅ Full test coverage with Pytest
- ✅ Structured according to MVC architecture

---

## Project Structure

```
app/
├── controllers/         # Business logic (user, doc, ingestion)
├── models/              # SQLAlchemy models (User, Document, Ingestion)
├── views/               # Route handlers (Blueprints)
├── schemas/             # Pydantic validation schemas
├── utils/               # LLM processing logic
├── test/                # All unit and route tests (pytest)
├── extensions.py        # DB, JWT, Migrate setup
├── config.py            # Config class (dev, prod)
└── __init__.py          # App factory
```

---

## Authentication & Authorization

- JWT-based login (`/api/users/login`)
- Token stores `id`, `email`, `role` as claims
- Protected routes use `@jwt_required()`
- Role-checking via manual claim checks:
  ```python
  if get_jwt()["role"] not in ["admin", "editor"]:
      return {"msg": "Forbidden"}, 403
  ```

---

## User Access Patterns

- **Register**: `POST /api/users/register`
- **Login**: `POST /api/users/login` → returns JWT
- **Profile**: `GET /api/users/me`
- **Change Role**: `PATCH /api/users/<id>` (admin-only)

### Model: `User`

| Field           | Type    | Constraints               |
| --------------- | ------- | ------------------------- |
| `id`            | Integer | Primary Key               |
| `email`         | String  | Unique, Validated         |
| `password_hash` | String  | Hashed, Required          |
| `role`          | String  | Enum: viewer/editor/admin |

---

## Document Management

- **Upload**: `POST /api/docs/upload`
- **List**: `GET /api/docs/`
- **Download**: `GET /api/docs/<doc_id>`
- **Delete**: `DELETE /api/docs/<doc_id>` (owner only)

### Model: `Document`

| Field        | Type    | Description             |
| ------------ | ------- | ----------------------- |
| `id`         | Integer | Primary Key             |
| `title`      | String  | Title of document       |
| `filename`   | String  | Stored filename on disk |
| `created_by` | Integer | ForeignKey → User.id    |

---

## Ingestion System

- **Trigger Ingestion**: `POST /api/ingestion/<doc_id>/trigger`
- **Get Ingestion Status**: `GET /api/ingestion/<id>/status`
- **List All Ingestions**: `GET /api/ingestion/`

### Model: `Ingestion`

| Field           | Type     | Description                         |
| --------------- | -------- | ----------------------------------- |
| `id`            | Integer  | Primary Key                         |
| `document_id`   | Integer  | FK → Document.id                    |
| `status`        | String   | queued / processing / done / failed |
| `summary`       | Text     | Output from LLM                     |
| `error_message` | Text     | Failure details if any              |
| `started_at`    | DateTime | Start time of ingestion             |
| `completed_at`  | DateTime | Completion time                     |

### Ingestion Flow:

- Stored as `queued`
- `threading.Thread` runs `process_document_ingestion()`
- Loads file from disk, sends to LLM API (e.g., Ollama)
- Saves back `summary`, updates status

---

## Testing

- Framework: `pytest`
- Tools: `pytest-cov`, `unittest.mock`
- Coverage: ~100%
- Test Modules:
  - `test_user_model.py`
  - `test_user_controller.py`
  - `test_user_routes.py`
  - `test_doc_controller.py`
  - `test_doc_routes.py`
  - `test_ingestion_controller.py`
  - `test_ingestion_routes.py`
  - `test_llm.py`

### Run Tests with Coverage:

```bash
pytest --cov=app --cov-report=term-missing --cov-config=.coveragerc
```

---

## Validation

- Email regex validation in model
- Role validation via `@validates`
- Pydantic schemas for all incoming requests

---

## Utilities

- `process_document_ingestion(app, doc_id)`: used in background thread
- Handles LLM call, status updates, error handling

---

## Deployment:

- will use EC2 instance
- in that EC2 instance , will up the application , then test tghe happy flow on that instance
- if everything works weel, take a AMI of that instance
- attach that image to an asg , and make enough instances up to meet all the throughput
- then there will be load balancer which will balance the load to asg
- and there will be a target group , and that target group will be map to route 53

## Futire scope:

- Add file type validation
- Rate limiting for ingestion endpoints
- Pagination for document list
- LLM response caching
- etc
