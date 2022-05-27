import pytest
import os
from prpy import world_files
from prpy.dumb_parse.rooms import RoomsFileParser

world_path = world_files.__path__._path[0]
rooms_path = os.path.join(world_path, 'ROOM')
def test_room_file():
    path = os.path.join(rooms_path, 'Midgard.room')
    rp = RoomsFileParser(path)
    assert rp
