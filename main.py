from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from room import Room
from action import Action
import base64
import pickle

class Server:
    def __init__(self):
        self.rooms = []
        self.status = "connexion"

    def findRoom(self, number):
        for room in self.rooms:
            if room.roomNumber == number:
                return room
        return None

    def createRoom(self,number):
        newRoom = Room(number)
        self.rooms.append(newRoom)
        print(f"The room {number} is created")


app = FastAPI()
server = Server()

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
    
@app.put("/login")
def update_item( item: Item):
    print(item)
    decoded_item=deserialize(item)
    print(decoded_item)
    if isinstance(decoded_item,Action) and decoded_item.type == "connect":
        nbPlayer = -1
        room = server.findRoom(decoded_item.info)
        if room is None:
            server.createRoom(decoded_item.info)
            nbPlayer = 0
        else:
            nbPlayer = room.playerConnected
            room.playerConnected += 1
            if nbPlayer + 1 >= room.nbPlayerMax:
                server.status = "play"
                print("lets play!!")
        return nbPlayer
    return 2

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    items[item_id] = item
    decoded_item=deserialize(item)
    print("lets get playing",decoded_item)
    return {"item_name": item.content, "item_id": item_id}

def serialize(data):
    item_data = "{\"content\": \""+base64.b64encode(pickle.dumps(data)).decode('utf-8')+"\"}"
    return item_data

def deserialize(data):
    return pickle.loads(base64.b64decode(data.content))