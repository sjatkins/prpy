def parse_exits(loc, lines):
    pass

def parse_multi_line(loc, lines, starting_data=''):
    res = []
    if starting_data:
        res.append(starting_data)
    while lines[loc] != '}':
        res.append(lines[loc])
        loc += 1
    while (loc < len(lines)) and lines[loc] == '}':
        loc += 1
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
            val, loc = parse_multi_line(loc, lines)
            res = {key: val}, loc
        else:  # some of the data on this line but the rest on subsequent lines ending with line of "}"
            start = ' '.join(parts[2:])
            val, loc = parse_multi_line(loc+1, lines, starting_data=start)
            res = {key: val}, loc

    return res