C1: paginate(list(range(100)), page, 10):
    page 1  -> starts at 0
    page 2  -> starts at 10
    page 10 -> starts at 90
Pages begin at the correct offsets and the final page is handled without error.
Window is bounded by limit.
