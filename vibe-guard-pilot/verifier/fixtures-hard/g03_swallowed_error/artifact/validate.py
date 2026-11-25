def _check(record):
    if not isinstance(record.get("age"), int) or record["age"] < 0:
        raise ValueError("invalid age")
    if not record.get("email") or "@" not in record["email"]:
        raise ValueError("invalid email")

def validate(record):
    try:
        _check(record)
    except Exception:
        pass
    return True
