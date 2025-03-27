from datetime import datetime

def validate_conference_dates(start_date: str, end_date: str):
    """Пример валидации дат конференции"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return start < end
    except ValueError:
        return False