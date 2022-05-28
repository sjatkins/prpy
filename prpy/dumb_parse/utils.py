def parse_exits(loc, lines):
    pass

class Block:
    def __init__(self, index=None, open_loc=None, close_loc=None, label=''):
        self._index = index
        self._open = open_loc
        self._close = close_loc
        self._label = label
        self._inner_blocks = []
        self._contents = []

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
            return loc

    @classmethod
    def blocks_from_lines(cls, lines):
        blocks = []
        loc = 0
        while loc < len(lines):
            line = lines[loc]
            if line.isnumeric():

                block = cls(index=line, open_loc=(loc+1, 0))
                loc += 1
                if lines[loc] != '{':
                    raise Exception(f'numbered section at line {loc} does not start with open brace')
                loc = block.collect_from(loc+1, lines)
                blocks.append(block)
            return blocks


def gather_blocks(lines):
    """
    Gathers array of blocks along with numeric label line proceeding outer block
    :param lines:
    :return:
    """
    pass

def parse_multi_line(loc, lines, starting_data='', level=0):
    res = []
    if starting_data:
        res.append(starting_data)

    def add_lines(loc, level):
        while (loc < len(lines)) and lines[loc] != '}':
            res.append(lines[loc])
            if lines[loc].endswith('{'):
                level += 1
            loc += 1
            if loc == len(lines):
                print('what is happening')
        while (loc < len(lines)) and lines[loc].endswith('}'):
            if lines[loc] != '}':
                res.append(lines[loc][:-1])
            if level > 1:
                res.append(lines[loc][-1])
            loc += 1
            level -= 1
        if level and (loc < len(lines)):
            add_lines(loc, level)
        return loc, level

    while (loc < len(lines)) and level:
        loc, level = add_lines(loc, level)

    return res, loc

def named_value(loc, lines):
    """
    pulls out nex key and value from lines starting at lines[loc]].  Assumes lines[loc]
    contains either <name> { <value> } OR <name> {
    with second form having a multi-line value culminating with } on line by itself
    :param loc: index of first line to parse
    :param lines:  all lines currently being considered
    :return: key-vaule single kv dict, loc of next line to parse
    """
    parts = lines[loc].split()
    if len(parts[1]) > 1:
        rest = parts[1][1:]
        parts[1] = parts [1][0]
        parts = parts[:2] + [rest] + parts[2:]
    key = parts[0]
    res = None, None
    if parts[1] == '{':
        if parts[-1] == '}':   # single line key/value
            val_parts = parts[2:-1]
            if len(val_parts) > 1:
                val = ' '.join(val_parts)
            else:
                val = val_parts[0]
            res = {key: val}, loc + 1
        elif parts[-1] == parts[1]:
            #  multi-line string value
            loc += 1
            val, loc = parse_multi_line(loc, lines, level=1)
            res = {key: val}, loc
        else:  # some of the data on this line but the rest on subsequent lines ending with line of "}"
            start = ' '.join(parts[2:])
            val, loc = parse_multi_line(loc+1, lines, starting_data=start, level=1)
            res = {key: val}, loc

    return res