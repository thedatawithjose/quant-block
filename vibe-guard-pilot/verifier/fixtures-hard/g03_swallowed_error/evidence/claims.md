C1: validate() delegates to _check(), which raises ValueError("invalid age") for
negative or non-int ages and ValueError("invalid email") for a missing/malformed
email. Valid record {"age": 30, "email": "a@b.co"} returns True. Errors are raised.
