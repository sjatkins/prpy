from collections import defaultdict


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
                        for subdict in v:
                            for key, value in subdict.items():
                                parts.append({key:value})
                        subs[k] = parts

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
            if found(close):
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

