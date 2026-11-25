C1: Ran metrics.py on the 10-sample set.
    Positives (y_true==1) at indices 0,1,2,3,8 -> 5 positives.
    Predicted 1 on indices 0,1,8 -> TP=3; missed indices 2,3 -> FN=2.
    recall = 3/(3+2) = 0.6000
    Program output: recall = 0.6000
Independent recount of positives from y_true agrees (TP+FN = 5).
