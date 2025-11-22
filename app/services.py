from typing import List, Optional
from app.models import Item, ItemCreate

items_db: List[Item] = []
next_id = 1

def create_item(item: ItemCreate) -> Item:
    """Create a new item."""
    global next_id
    new_item = Item(id=next_id, **item.dict())
    items_db.append(new_item)
    next_id += 1
    return new_item

def get_item(item_id: int) -> Optional[Item]:
    """Get an item by ID."""
    for item in items_db:
        if item.id == item_id:
            return item
    return None

def get_items() -> List[Item]:
    """Get all items."""
    return items_db

def update_item(item_id: int, item_update: ItemCreate) -> Optional[Item]:
    """Update an existing item."""
    for item in items_db:
        if item.id == item_id:
            item.name = item_update.name
            item.description = item_update.description
            return item
    return None

def delete_item(item_id: int) -> bool:
    """Delete an item by ID."""
    global items_db
    items_db = [item for item in items_db if item.id != item_id]
    return True
