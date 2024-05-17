from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

class Server:
    def __init__(self):
        self.rooms = []

class Item(BaseModel):
    content: bytes

if __name__ == '__main__':
    server = Server()

    @app.get("/")
    def read_root():
        return {"Hello": "World"}

    @app.get("/items/{item_id}")
    def read_item(item_id: int):
        if item_id in server.items:
            return server.items[item_id]
        else:
            raise HTTPException(status_code=404, detail="Item not found")

    @app.put("/items/{item_id}")
    def update_item(item_id: int, item: Item):
        print(item)

        return {"item_name": item.name, "item_id": item_id}

    while True:
        print(server.items)
