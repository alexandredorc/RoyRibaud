from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from room import Room
from action import Action
from network import serialize, deserialize

class Server:
    def __init__(self):
        self.rooms = []

    def findRoom(self, number):
        for room in self.rooms:
            if room.roomNumber == number:
                return room
        return None

    def createRoom(self,number):
        newRoom = Room(number)
        self.room.append(newRoom)
        print(f"The room {number} is created")
        

app = FastAPI()
server = Server()


class Item(BaseModel):
    content: bytes

items: Dict[int, Item] = {}

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id in server.items:
        print(item_id)
        return server.items[item_id]
    else:
        raise HTTPException(status_code=404, detail="Item not found")

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    print(item,item_id)
    print(items[item_id])
    if isinstance(items[item_id],Action) and items[item_id].type == "create":
        server.createRoom(items[item_id].info)
    return {"item_name": item.name, "item_id": item_id}