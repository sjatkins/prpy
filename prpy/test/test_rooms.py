import pytest
import os
from prpy import world_files
from prpy.parsing.rooms import RoomsFileParser, convert_all_to_json

world_path = world_files.__path__._path[0]
rooms_path = os.path.join(world_path, 'ROOM')

def test_room_file():
    path = os.path.join(rooms_path, 'Void.room')
    rp = RoomsFileParser(path)
    assert rp
#    rp.write_json()

def test_convert_all():
   convert_all_to_json()
