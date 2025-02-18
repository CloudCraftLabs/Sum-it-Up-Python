from datetime import datetime, timezone, timedelta, date
from src.utils.common import constants

def get_timestamp_utcnow(return_type=None):
    if return_type is None:
        return_type="int"
    if return_type.lower() in ["int"]:
        return int(datetime.utcnow().timestamp())
    else:
        return datetime.utcnow().timestamp()

   
def get_datetime_utcnow(flag=None):
    if flag is None:
        flag = "datetime"
    if flag.lower() in ["datetime"]:
        return datetime.utcnow()
    elif flag.lower() in ["date"]:
        return datetime.utcnow().date()

def get_datetime_db_format():
    return datetime.strftime(get_datetime_utcnow(), constants.DB_DATE_FORMAT)


def datetime_to_date(datetime_format=None, timezone_data=None):
    try:
        timezoned_datetime = datetime(datetime.now(timezone.utc).year, 1, 1, 0, 0)
        if datetime_format in [None]:
            datetime_format = timezoned_datetime
        if isinstance(datetime_format, datetime):
            updated_datetime = datetime_format + timedelta(hours=timezone_data)
            timezoned_datetime = datetime.strftime(updated_datetime, constants.UI_DATE_FORMAT)
        elif isinstance(datetime_format, str):
            updated_datetime = datetime.strptime(datetime_format, constants.DB_DATE_FORMAT) + timedelta(hours=timezone_data)
            timezoned_datetime = datetime.strftime(updated_datetime, constants.UI_DATE_FORMAT)
        elif isinstance(datetime_format, date):
            updated_datetime = datetime(datetime_format.year, datetime_format.month, datetime_format.day) + timedelta(hours=timezone_data)
            timezoned_datetime = datetime.strftime(updated_datetime, constants.UI_DATE_FORMAT)
        return timezoned_datetime
    except Exception as e:
        raise e