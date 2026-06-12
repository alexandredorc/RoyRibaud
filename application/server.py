from domain.room import Room


class Server:
    def __init__(self):
        self.rooms = {}

    def find_room(self, number):
        return self.rooms.get(number)

    def get_or_create_room(self, number):
        room = self.find_room(number)
        if room is None:
            room = Room(number)
            self.rooms[number] = room
            print(f"Room {number} created")
        return room
