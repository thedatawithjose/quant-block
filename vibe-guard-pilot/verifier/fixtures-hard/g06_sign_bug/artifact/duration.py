def _minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)

def duration_minutes(start, end):
    s, e = _minutes(start), _minutes(end)
    if e < s and s - e > 12 * 60:
        e += 24 * 60
    return e - s
