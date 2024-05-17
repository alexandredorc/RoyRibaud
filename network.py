import pickle
import base64
import requests

class Network:
    def __init__(self, server="0.0.0.0", room=1):
        self.uri = f"{server}/items/{room}"
        self.room = room
    
    def send(self,data):
        response_put = requests.put(self.uri, json=serialize(data))

        if response_put.status_code == 200 or response_put.status_code == 500:
            return 1
        else:
            print("PUT request failed")
            print("Status code:", response_put.status_code)
            print("Response:", response_put.text)
            return 0

    def get(self):
        response_get = requests.get(self.uri)
        if response_get.status_code == 200:
            return deserialize(response_get.json())
        else:
            print("GET request failed")
            print("Status code:", response_get.status_code)
            print("Response:", response_get.text)
            return 0
            
def serialize(data):
    item_data = {"content": base64.b64encode(pickle.dumps(data)).decode('utf-8')}
    return item_data

def deserialize(data):
    return pickle.loads(base64.b64decode(data['content']))