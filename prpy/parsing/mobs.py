import json, os
from prpy.parsing.utils import Block
from prpy import json_world
from prpy import world_files

class MobsFileParsere:
    def __init__(self, path):
        self._path = path
        self._zone = os.path.basename(path).split('.')[0]
        with open(path) as f:
            lines = [l.strip() for l in f.readlines()]
        self._lines = [l for l in lines if l and (not l.startswith('//'))]
        loc = 0
        self._mobs = self.mobs_from_blocks()

    def as_dict(self):
        return dict(
            zone = self._zone,
            mobs = self._mobs
        )

    def mob_from_block(self, block):
        mob = block.as_dict()
        mob['zone'] = self._zone
        return mob

    def mobs_from_blocks(self):
        blocks = Block.blocks_from_lines(self._lines)
        return [self.mob_from_block(b) for b in blocks]
