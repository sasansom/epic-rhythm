KNOWN_SEDES = ("1", "2", "2.5", "3", "4", "4.5", "5", "6", "6.5", "7", "8", "8.5", "9", "10", "10.5", "11", "12")

def is_metrically_permissible(shape, sedes):
    """Returns True iff shape is metrically permitted at sedes."""
    s = (sedes - 1) * 2
    if s != int(s) or s < 0 or s > 24:
        raise ValueError("invalid sedes {sedes}")
    if s == 23 or s % 4 not in (0, 2, 3):
        return False
    for c in shape:
        s += {"⏑": 1, "–": 2}[c]
        if s > 24 or s == 23 or s % 4 not in (0, 2, 3):
            return False
    return True
