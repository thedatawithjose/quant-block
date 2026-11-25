THRESHOLD = 0.7

def decide(score, threshold=THRESHOLD):
    if score > threshold:
        return {"accepted": False, "reason": "score exceeds threshold"}
    return {"accepted": True, "reason": "within limit"}
