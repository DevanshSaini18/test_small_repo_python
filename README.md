# Small FastAPI Backend

This is a small example of a FastAPI backend with CRUD operations for items.

## Setup

1. Install Poetry if not already installed: https://python-poetry.org/docs/#installation

2. Install dependencies:
   ```
   poetry install
   ```

3. Run the application:
   ```
   poetry run python main.py
   ```

Or using uvicorn:
   ```
   poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

- POST /api/v1/items/ - Create item
- GET /api/v1/items/{item_id} - Get item
- GET /api/v1/items/ - Get all items
- PUT /api/v1/items/{item_id} - Update item
- DELETE /api/v1/items/{item_id} - Delete item

Visit http://localhost:8000/docs for interactive API docs.
