# File Uploads & Attachments

This document describes how file attachments are represented and configured in the codebase — the database model, the API schemas, and the environment settings that control upload storage and limits.

## Data model (app/models.py)
- Attachment table: attachments
- Columns:
  - id (int, PK)
  - filename (string) — original filename
  - file_path (string) — server-side path or storage key where the file is stored
  - file_size (int) — bytes
  - mime_type (string)
  - item_id (FK -> items.id) — association to the Item the attachment belongs to
  - uploaded_by_id (FK -> users.id) — user who uploaded the file
  - created_at (datetime)
- Relationships:
  - item: relationship back_populates "attachments" on Item; Attachment.item points to the parent Item
  - uploaded_by: relationship to User
- Referential behavior:
  - Attachment.item_id is defined with ondelete="CASCADE" on the items FK, so attachments are deleted when their item is removed.
  - Item model declares attachments = relationship("Attachment", back_populates="item", cascade="all, delete-orphan")

## API / Validation schema (app/schemas.py)
- AttachmentRead Pydantic model (read-only representation):
  - id, filename, file_size, mime_type, item_id, uploaded_by_id, created_at
  - orm_mode = True
- Note: ItemRead (the primary item response schema) in the current schemas does not include an attachments list field even though the Item model has an attachments relationship; AttachmentRead exists to represent attachment resources when returned by an endpoint or service.

## Application-level usage (app/services.py, app/models.py)
- The services module imports the Attachment model, indicating intended service-level handling, but there are no explicit create/download/delete attachment helper functions implemented in the service layer in the current code snapshot.
- The Attachment model is integrated into the domain: Items have attachments and attachments are associated with Users (uploaded_by).

## Configuration ( .env.example )
- File upload configuration variables are provided in .env.example:
  - MAX_UPLOAD_SIZE_MB=10 — maximum upload size (MB)
  - UPLOAD_DIR=./uploads — default local filesystem upload directory
- These variables reflect how uploads are expected to be constrained and where files should be stored by an upload implementation.

## Project documentation references (README.md)
- README lists "File attachments (coming soon)" under Collaboration, indicating attachment functionality is planned/partially modeled but not fully exposed via endpoints at present.

## Summary of current state
- Persistent model: Attachments are fully modeled in the database with fields to store metadata and storage pointers, and are linked to items and users with cascade delete behavior.
- Validation/output: AttachmentRead exists to serialize attachment records.
- Config: Upload size and directory are configurable via environment variables.
- Service/API: The model and schema are present; explicit attachment CRUD endpoints and service helpers are not implemented in routes.py/services.py in the provided snapshot.

Relevant files
- app/models.py — Attachment model, Item relationship, cascade behavior
- app/schemas.py — AttachmentRead schema
- .env.example — MAX_UPLOAD_SIZE_MB and UPLOAD_DIR configuration variables
- app/services.py — Attachment model imported (indicates service-level intent)
- README.md — high-level note about file attachments (coming soon)


## Source Files
- app/models.py
- app/schemas.py
- .env.example
- app/services.py
- README.md