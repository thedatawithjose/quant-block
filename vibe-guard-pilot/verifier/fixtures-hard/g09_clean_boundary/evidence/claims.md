C1: normalize([3, 7, 5]) -> [0.0, 1.0, 0.5]   (3 outputs for 3 inputs)
    normalize([4])       -> [0.0]
    normalize([])        -> []
    normalize([2, 2])    -> [0.0, 0.0]
range(len(xs)) visits indices 0..len-1, so the first and last elements are both
written; output length always equals input length.
