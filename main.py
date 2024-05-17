from typing import Union, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    content: bytes

# In-memory storage for items
items: Dict[int, Item] = {}

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id in items:
        return items[item_id]
    else:
        raise HTTPException(status_code=404, detail="Item not found")

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    items[item_id] = item
    return {"item_name": item.name, "item_id": item_id}

# To run the server, use the command: uvicorn main:app --host 0.0.0.0 --port 8000
