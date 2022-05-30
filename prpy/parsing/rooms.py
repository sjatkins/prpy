import json, os
from prpy.parsing.utils import Block
from prpy import json_world
from prpy import world_files
import logging

logger = logging.getLogger('rooms')

class RoomsFileParser:
    def __init__(self, path):
        self._path = path
        with open(path) as f:
            lines = [l.strip() for l in f.readlines()]
        self._lines = [l for l in lines if l and (not l.startswith('//'))]
        self._zone, loc = self.parse_offset()
        self._lines = self._lines[loc:]
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
        try:
            room = block.as_dict()
            room['zone'] = self._zone
            room['room_key'] = self.expanded_room(str(block._index))
            self.parse_special(room)
            return room
        except Exception as e:
            print(f'block {block._index} exception {e}')

    def rooms_from_blocks(self):
        blocks = Block.blocks_from_lines(self._lines)
        return [self.room_from_block(b) for b in blocks]


    def parse_offset(self):
        loc = 0
        key = "#offset "
        while not self._lines[loc].startswith(key):
            loc += 1
        line = self._lines[loc]
        if line.startswith(key):
            return line[len(key):], loc+1


def convert_all_to_json(source_path=None, json_path=None):
    def room_path(module):
        path = module.__path__._path[0]
        return os.path.join(path, 'ROOM')

    if not source_path:
        source_path = room_path(world_files)
    if not json_path:
        json_path = room_path(json_world)

    source_files = [f for f in os.listdir(source_path) if f.endswith('.room')]
    for fn in sorted(source_files):
        print('converting', fn)
        src_path = os.path.join(source_path, fn)
        base = fn.split('.')[0]
        json_fn = f'{base}.json'
        target_path = os.path.join(json_path, fn)
        try:
            rp = RoomsFileParser(src_path)
            rp.write_json(json_dir=json_path)
        except Exception as e:
            print(f'exception in {fn}: {e}')
