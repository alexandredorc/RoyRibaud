from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from network import Network

class Server:
    def __init__(self):
        self.rooms = []


app = FastAPI()
server = Server()
n=Network()

class Item(BaseModel):
    content: bytes


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id in server.items:
        print(item_id)
        return server.items[item_id]
    else:
        raise HTTPException(status_code=404, detail="Item not found")

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    print(item,item_id)

    return {"item_name": item.name, "item_id": item_id}

while True:
    print(server.items)
