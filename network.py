import pickle
import base64

import requests

# URL of the FastAPI server
base_url = "https://royribaud.onrender.com"
# Data to be sent in the PUT request
item_data = {
    "name": "Test Item",
    "price": 15.99,
    "is_offer": True
}

class Network:
    def __init__(self, server=base_url, room=1, player_id=0):
        get_url = f"{base_url}/items/{room}"
        self.room = room
        self.player_id = player_id
        self.uri = f"{get_url}"
        print(self.uri)
        self.websocket = None
        self.p = None

    def serialize(self,data):
        return base64.b64encode(data).decode('utf-8')
    
    def send(self,data):
        bit_data= pickle.dumps(data)
        item_data = {
            "content": self.serialize(bit_data)
        }
        print(item_data)
        response_put = requests.put(self.uri, json=item_data)

        if response_put.status_code == 200:
            print("PUT request successful")
            print("Response:", response_put.json())
            print(pickle.loads(response_put.json().content))
        else:
            print("PUT request failed")
            print("Status code:", response_put.status_code)
            print("Response:", response_put.text)

    def get(self):
        
        response_get = requests.get(self.uri)
        if response_get.status_code == 200:
            print("GET request successful")
            print("Response:", response_get.json())
        else:
            print("GET request failed")
            print("Status code:", response_get.status_code)
            print("Response:", response_get.text)
            
        return 0

    def getP(self):
        return self.p
print("init")
n=Network(base_url)
print("send")
data=[0,0,0,12]
n.send(data)

print("get")
print(n.get())