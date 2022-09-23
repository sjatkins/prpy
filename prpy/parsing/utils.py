from collections import defaultdict
import json, os
from prpy import json_world
from prpy import world_files

class Block:
    def __init__(self, index=None, open_loc=None, close_loc=None, label=''):
        self._index = index
        self._open = open_loc
        self._close = close_loc
        self._label = label
        self._inner_blocks = []
        self._contents = []

    def contents(self):
        return self._contents[0] if (len(self._contents) == 1) else self._contents

    def as_dict(self):
        res = {}
        def process_sub_blocks():

            all_labels = [b._label for b in self._inner_blocks]
            unique_labels = set(all_labels)
            if len(unique_labels) < len(all_labels):
                return [b.as_dict() for b in self._inner_blocks]
            else:
                subs = {}
                for block in self._inner_blocks:
                    subs.update(block.as_dict())
                return subs

        if self._index:
            res['index'] = self._index
            subs = process_sub_blocks()
            if isinstance(subs, list):
                # special case block top level duplicate fields handling
                fixed = defaultdict(list)
                for item in subs:
                    k,v = list(item.items())[0]
                    fixed[k].append(v)
                subs = {}
                for k,v in fixed.items():
                    if len(v) == 1:
                        subs[k] = v[0]
                    else:
                        parts = []
                        if isinstance(v, dict):
                            for subdict in v:
                                for key, value in subdict.items():
                                    parts.append({key:value})
                            subs[k] = parts
                        elif isinstance(v, str):
                            unique = {x for x in v}
                            if len(unique) == 1:
                                subs[k] = [unique]
                            else:
                                comma_lists = all((',' in x for x in unique))
                                join_char = ',' if comma_lists else ''
                                subs[k] = join_char.join(unique)


            res.update(subs)
        elif self._label is not None:
            contents = self.contents()
            if contents:
                res[self._label] = contents
            else:
                res[self._label] = process_sub_blocks()

        return res

    def collect_from(self, loc, lines):
        complete = False
        found = lambda f: f != -1
        while not complete:
            line = lines[loc]
            open = line.find('{')
            close = line.find('}')
            if found(open):
                if (open > 0) and line[open-1] == '#':
                    self._contents.append(line)
                    loc += 1
                    continue
                o_loc = (loc, open)
                label = line[:open].strip()
                after_open = line[open+1:]
                block = self.__class__(open_loc=o_loc, label=label)
                if found(close) and line.endswith('}'):
                    block._contents.append(line[open+1:close].strip())
                    block._close = (loc, close)
                    loc += 1
                else:
                    if after_open:
                        block._contents.append(after_open)
                    loc = block.collect_from(loc+1, lines)
                self._inner_blocks.append(block)
                continue
            if found(close) and line[-1] == '}':
                self._close = (loc, close)
                if close != 0:
                    self._contents.append(line[:close])
                complete = True
                loc += 1
                return loc
            # just gather
            self._contents.append(line)
            loc += 1

    @classmethod
    def blocks_from_lines(cls, lines):
        blocks = []
        loc = 0
        while loc < len(lines):
            line = lines[loc]
            if line.startswith('//'):
                loc += 1
                continue
            if line.isnumeric():

                block = cls(index=line, open_loc=(loc+1, 0))
                loc += 1
                if lines[loc] != '{':
                    raise Exception(f'numbered section at line {loc} does not start with open brace')
                loc = block.collect_from(loc+1, lines)
                if loc < len(lines):
                    line = lines[loc]
                blocks.append(block)
        return blocks


def convert_all_to_json(file_parser, src_type, source_path=None, json_path=None):
    def src_path(module):
        path = module.__path__._path[0]
        return os.path.join(path, src_type)

    if not source_path:
        source_path = src_path(world_files)
    if not json_path:
        json_path = src_path(json_world)

    source_files = [f for f in os.listdir(source_path) if f.endswith('.room')]
    for fn in sorted(source_files):
        print('converting', fn)
        src_path = os.path.join(source_path, fn)
        base = fn.split('.')[0]
        json_fn = f'{base}.json'
        target_path = os.path.join(json_path, fn)
        try:
            parsed = file_parser(src_path)
            parsed.write_json(json_dir=json_path)
        except Exception as e:
            print(f'exception in {fn}: {e}')