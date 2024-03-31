from datetime import datetime, timezone

def start_of_day_timestamp() -> float:
    today = datetime.today()
    return datetime(today.year, today.month, today.day).timestamp()

def should_generate_row(timestamp : float, include_today : bool) -> bool:
    if timestamp < start_of_day_timestamp():
        return True
    elif timestamp == start_of_day_timestamp():
        if include_today == True:
            return True
    return False

