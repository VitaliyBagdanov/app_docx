from datetime import datetime

MONTHS = [
    '', 'января', 'февраля', 'марта', 'апреля', 'мая',
    'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
]

def format_russian_date(value):
    if isinstance(value, str):
        try:
            val = datetime.fromisoformat(value)
        except Exception:
            return value
    elif isinstance(value, datetime):
        val = value
    else:
        return value
    day = val.day
    month = MONTHS[val.month]
    year = val.year
    return f"{day:02d} {month} {year} года"
