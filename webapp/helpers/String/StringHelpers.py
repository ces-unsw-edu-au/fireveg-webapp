import secrets
from datetime import datetime, timedelta

def generate_random_string_using_time():
    random_code = secrets.token_hex(8)
    timestamp = int(datetime.timestamp(datetime.now()))
    generated_string = f"{random_code}-{timestamp}"
    return generated_string

def add_seconds_to_current_date_time(seconds):
    current_date_time = datetime.now()
    updated_date_time = current_date_time + timedelta(seconds=seconds)
    return updated_date_time

def add_days_to_current_date_time(days):
    current_date_time = datetime.now()
    updated_date_time = current_date_time + timedelta(days=days)
    return updated_date_time
