from datetime import datetime


def convert_str_to_datetime(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f%z')
