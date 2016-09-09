default_names = {'Reggie_Chode', 'Mo_Dick'}


def name_gen():
    """
    Yields a name from the used_names dict. Will append a unique 
    incremental # if the name has already been used.
    """
    inc = 0
    while True:
        for name in default_names:
            yield name + str(inc) if inc else name
        inc += 1


ng = name_gen()

def get_name():
    return ng.__next__()

