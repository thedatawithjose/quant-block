def paginate(items, page, limit):
    if page < 1 or limit < 1:
        raise ValueError("page and limit must be >= 1")
    start = (page - 1) * limit
    end = start + limit + 1
    return items[start:end]
