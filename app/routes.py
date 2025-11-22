from fastapi import APIRouter, HTTPException
from typing import List

from app.models import Item, ItemCreate
from app.services import create_item, get_item, get_items, update_item, delete_item

router = APIRouter()

@router.post("/items/", response_model=Item)
def create_new_item(item: ItemCreate):
    """Create a new item."""
    return create_item(item)

@router.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    """Read an item by ID."""
    item = get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.get("/items/", response_model=List[Item])
def read_items():
    """Read all items."""
    return get_items()

@router.put("/items/{item_id}", response_model=Item)
def update_existing_item(item_id: int, item: ItemCreate):
    """Update an item."""
    updated_item = update_item(item_id, item)
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item

@router.delete("/items/{item_id}")
def delete_existing_item(item_id: int):
    """Delete an item."""
    if not delete_item(item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    return {"detail": "Item deleted"}
