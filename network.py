import asyncio
import websockets
import pickle

class Network:
    def __init__(self, server="192.168.100.174", port=5555, player_id=0):
        self.server = server
        self.port = port
        self.player_id = player_id
        self.uri = f"ws://{self.server}:{self.port}/ws/{self.player_id}"
        self.websocket = None
        self.p = None

    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.uri)
            self.p = pickle.loads(await self.websocket.recv())
            return self.p
        except Exception as e:
            print(f"Error connecting: {e}")

    async def send(self, data):
        try:
            await self.websocket.send(pickle.dumps(data))
            reply = pickle.loads(await self.websocket.recv())
            return reply
        except Exception as e:
            print(f"Error sending data: {e}")

    async def close(self):
        if self.websocket:
            await self.websocket.close()

    def getP(self):
        return self.p

# Example usage
async def main():
    network = Network(player_id=0)  # or player_id=1 for the second player
    await network.connect()
    player = network.getP()
    print("Initial player state:", player)
    
    # Example of sending player data and receiving a reply
    updated_player = player  # Modify player as needed
    response = await network.send(updated_player)
    print("Received updated state of the other player:", response)
    
    await network.close()

# Run the example
asyncio.run(main())
