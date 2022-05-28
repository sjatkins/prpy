import json, os
from prpy.dumb_parse.utils import Block

class RoomsFileParser:
    def __init__(self, path):
        self._path = path
        with open(path) as f:
            lines = [l.strip() for l in f.readlines()]
        self._zone = self.parse_offset(lines[0])
        self._lines = [l for l in lines[1:] if l]
        self._special = dict(exits= self.parse_room_exits)
        self._rooms = self.rooms_from_blocks()

    def as_dict(self):
        return dict(
            zone = self._zone,
            rooms = self._rooms
        )

    def write_json(self, json_dir='', as_dict=True, dict_key='index'):
        base = os.path.basename(self._path)
        fname = f'{base.split(".")[0]}.json'
        out_path = os.path.join(json_dir, fname)
        basics = self.as_dict()
        if as_dict:
            room_dict = {r[dict_key]: r for r in basics['rooms']}
            basics['rooms'] = room_dict

        with open(out_path, 'w') as f:
            json.dump(basics, f)

    def expanded_room(self, room_spec):
        return f'{self._zone}:{room_spec}' if room_spec.isnumeric() else room_spec

    def parse_room_exits(self, exits):
        """
        For each exit return dictionary of direction, room_specifier, and optional keywords dict.
        Room specifier will always be of form <zone>:<room_number>.
        Note that some 'directions' are a number from 10-13 which is yet to be further parsed
        :param exit_lines: The raw data specifying exits
        :return: list of exit dicts as specified above
        """
        res = []
        current = None
        by_to = []
        if isinstance(exits, dict):
            exits = [exits]
        for exit in exits:
            if isinstance(exit, str):
                print ('something is very wrong')
            to = exit.get('to')
            if to:
                by_to.append([exit])
            else:
                by_to[-1].append(exit)

        for exit_def in by_to:
            to = exit_def[0].get('to')
            direction, room_spec = [x.strip() for x in to.split(',')]
            exit = {'direction': direction, 'room': self.expanded_room(room_spec)}
            for exit_extra in exit_def[1:]:
                exit.update(exit_extra)
            res.append(exit)

        return res

    def parse_special(self, room_dict):
        for key, fn in self._special.items():
            val = room_dict.pop(key, None)
            if val is not None:
                room_dict[key] = fn(val)


    def room_from_block(self, block):
        room = block.as_dict()
        room['zone'] = self._zone
        room['room_key'] = self.expanded_room(str(block._index))
        self.parse_special(room)
        return room


    def rooms_from_blocks(self):
        blocks = Block.blocks_from_lines(self._lines)
        return [self.room_from_block(b) for b in blocks]


    def parse_offset(self, line):
        key = "#offset "
        if line.startswith(key):
            return line[len(key):]

