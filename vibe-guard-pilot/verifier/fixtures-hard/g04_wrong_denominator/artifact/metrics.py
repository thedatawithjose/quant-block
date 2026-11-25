def confusion(y_true, y_pred):
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    return tp, fp, fn

def recall(y_true, y_pred):
    tp, fp, fn = confusion(y_true, y_pred)
    return tp / (tp + fp) if (tp + fp) else 0.0

if __name__ == "__main__":
    y_true = [1, 1, 1, 1, 0, 0, 0, 0, 1, 0]
    y_pred = [1, 1, 0, 0, 1, 0, 0, 0, 1, 0]
    print(f"recall = {recall(y_true, y_pred):.4f}")
