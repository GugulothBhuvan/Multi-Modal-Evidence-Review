from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def compute_metrics(y_true, y_pred, labels):
    acc = accuracy_score(y_true, y_pred)
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, labels=labels, zero_division=0)
    return {
        "accuracy": acc,
        "precision": p.tolist(),
        "recall": r.tolist(),
        "f1": f1.tolist(),
        "labels": labels
    }
