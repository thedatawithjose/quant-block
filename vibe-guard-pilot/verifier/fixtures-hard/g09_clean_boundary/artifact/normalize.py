def normalize(xs):
    out = [0.0] * len(xs)
    if not xs:
        return out
    lo, hi = min(xs), max(xs)
    span = hi - lo
    for i in range(len(xs)):
        out[i] = 0.0 if span == 0 else (xs[i] - lo) / span
    return out
