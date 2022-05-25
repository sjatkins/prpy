from typing import List, Optional, Any
from pydantic import BaseModel

class RoomExit(BaseModel):
    direction: str
    room_label: str

class Room(BaseModel):
    index: int
    offset: str
    sector: str
    desc: str
    flags: Optional[List[str]]
    exits: List[RoomExit]

class RoomOffset(BaseModel):
    name: str
    rooms: List[Room]

class RoomsFileParser:
    def __init__(self, path):
        self._path = path
        with open(path) as f:
            lines = [l.strip() for l in f.readlines()]
            self._offset = self.parse_offset(lines[0])
            self._lines = lines[1:]
        self._rooms = self.parse_rooms()

    def parse_room(self, lines):
        index = int(lines[0])
        g_lines = (l for l in lines[2:-1])  # skip open-close brace lines
        name = ''
        desc_lines = []
        def parse_name(line):
            pass
        def parse_desc(data):
            pass
        for line in g_lines:
            if line.startswith('name'):
                name = parse_name(line)
            elif line.startswith('desc'):
                pass


        pass

    def parse_rooms(self):
        res = []
        room_data = self.room_lines()
        for room in room_data:
            res.append(self.parse_room(room))
    def room_lines(self):
        res = []
        curr_room = []
        for l in self._lines:
            if not l:
                if curr_room:
                    res.append(curr_room)
                    curr_room = []
            else:
                curr_room.append(l)
        if curr_room:
            res.append(curr_room)

        return res


    def parse_offset(self, line):
        key = "#offset "
        if line.startswith(key):
            return line[len(key):]

    def parse_rooms(self):
        offset = self.parse_offset(self._lines[0])

