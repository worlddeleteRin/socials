def can_be_numeric(v: str | int):
    if isinstance(v, int):
        return True
    if isinstance(v, str):
        return v.isnumeric()
    return False
