from typing import List, Optional, Any
from pydantic import BaseModel
from prpy.dumb_parse.utils import named_value

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
        self._zone = self.parse_offset(lines[0])
        self._lines = [l for l in lines[1:] if l]
        self._special = dict(exits= self.parse_room_exits)
        self._rooms = self.parse_rooms()

    def expanded_room(self, room_spec):
        return f'{self._zone}:{room_spec}' if room_spec.isnumeric() else room_spec

    def parse_room_exits(self, exit_lines):
        """
        For each exit return dictionary of direction, room_specifier, and optional keywords dict.
        Room specifier will always be of form <zone>:<room_number>.
        Note that some 'directions' are a number from 10-13 which is yet to be further parsed
        :param exit_lines: The raw data specifying exits
        :return: list of exit dicts as specified above
        """
        res = []
        loc = 0

        def process_to(loc, lines, room_spec):
            direction, room = [v.strip() for v in room_spec.split(',')]
            expanded = dict(direction=direction, room=self.expanded_room(room))
            loc += 1
            while loc < len(lines):
                mv, loc = named_value(loc, exit_lines)
                if 'to' in mv:
                    loc -= 1
                    break
                expanded.update(mv)
                #loc += 1
            return expanded, loc

        while loc < len(exit_lines):
            kv,_ = named_value(loc, exit_lines)
            _, room_spec = list(kv.items())[0]
            expanded, loc = process_to(loc, exit_lines,room_spec)
            res.append(expanded)

        return res

    def parse_special(self, room_dict):
        for key, fn in self._special.items():
            val = room_dict.pop(key, None)
            if val is not None:
                room_dict[key] = fn(val)



    def parse_room(self, lines):
        index = int(lines[0])
        if index == 600:
            print('trouble')
        print(f'processing room {index}')
        g_lines = [l for l in lines[2:-1]]  # skip open-close brace lines
        loc = 0
        room = {'index': index, 'zone': self._zone, 'room_key': self.expanded_room(str(index))}
        while loc < len(g_lines):
            kv, loc = named_value(loc, g_lines)
            room.update(kv)
        self.parse_special(room)
        return room

    def parse_rooms(self):
        res = []
        room_data = self.room_lines()
        for room in room_data:
            res.append(self.parse_room(room))
        return res

    def room_lines(self):
        res = []
        curr_room = []
        for l in self._lines:
            if l.isnumeric():
                if curr_room:
                    res.append(curr_room)
                curr_room = [l]
            else:
                curr_room.append(l)
        if curr_room:
            res.append(curr_room)

        return res


    def parse_offset(self, line):
        key = "#offset "
        if line.startswith(key):
            return line[len(key):]

