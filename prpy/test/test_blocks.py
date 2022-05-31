import os
from prpy import world_files
from prpy.parsing.utils import Block

world_path = world_files.__path__._path[0]
rooms_path = os.path.join(world_path, 'ROOM')
mobs_path = os.path.join(world_path, 'MOB')

# def test_room_blocks():
#     path = os.path.join(rooms_path, 'Midgard.room')
#     with open(path) as f:
#         lines = [l.strip() for l in f.readlines()]
#         lines = [l for l in lines[1:] if l]
#     blocks = Block.blocks_from_lines(lines)
#     assert blocks

def test_mob_blocks():
    path = os.path.join(mobs_path, 'Arachnos.mob')
    with open(path) as f:
        lines = [l.strip() for l in f.readlines()]
        lines = [l for l in lines if l]
    blocks = Block.blocks_from_lines(lines)
    assert blocks
