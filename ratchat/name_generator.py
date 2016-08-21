used_names = {
    'Reggie Chode': None,
    'Mo Dick': None
}


def name_gen():
    while True:
        for name in used_names.keys():
            yield name + str(used_names[name]) if used_names[name] else name
            used_names[name] = used_names[name] + 1 if used_names[name] else 1


ng = name_gen()

def get_name():
    return ng.__next__()

