import datetime
import time
from datetime import timedelta

import dateutil
import pytz

from flaskd3.common.constants import DayOfWeek
from flaskd3.common.exceptions import ValidationException

tzlocal = pytz.timezone("Asia/Kolkata")
tzutc = pytz.utc
DELTA = timedelta(days=1)
datetime_format = "%Y-%m-%dT%H:%M:%S%z"
date_format = "%Y-%m-%d"
time_format = "%H:%M:%S"
datetime_format_hr = "%I:%M %p %d-%m-%Y"
time_format = "%H:%M:%S"

country_code_to_tz_map = {
    "IN": "Asia/Kolkata",
    "UAE": "Asia/Dubai"
}

region_id_to_tz_map = {
    "IN": "Asia/Kolkata",
    "UAE": "Asia/Dubai"
}

next_day_of_week_map = {
    DayOfWeek.MONDAY: DayOfWeek.TUESDAY,
    DayOfWeek.TUESDAY: DayOfWeek.WEDNESDAY,
    DayOfWeek.WEDNESDAY: DayOfWeek.THURSDAY,
    DayOfWeek.THURSDAY: DayOfWeek.FRIDAY,
    DayOfWeek.FRIDAY: DayOfWeek.SATURDAY,
    DayOfWeek.SATURDAY: DayOfWeek.SUNDAY,
    DayOfWeek.SUNDAY: DayOfWeek.MONDAY,
}


def local_timezone():
    return tzlocal


def utcnow():
    return datetime.datetime.now(pytz.utc)


def current_datetime(tz=None):
    if not tz:
        return datetime.datetime.now(tzlocal)
    else:
        return datetime.datetime.now(tz)


def is_naive(date_time):
    return date_time.tzinfo is None or date_time.tzinfo.utcoffset(date_time) is None


def to_date(date_time, local_tz=None):
    """
    Converts the datetime object into date object in local timezone.
    Fails if the datetime in naive.

    Examples:
        >>> aware = datetime.datetime(2011, 8, 15, 18, 40, 0, 0, pytz.UTC)
        >>> unaware = datetime.datetime(2011, 8, 15, 18, 40, 0, 0)   # This is considered as UTC
        >>> dateutils.to_date(aware)
        datetime.date(2011, 8, 16)
        >>> dateutils.to_date(unaware)
        datetime.date(2011, 8, 16)
        >>> aware = datetime.datetime(2011, 8, 15, 18, 40, 0, 0, pytz.timezone('Asia/Kolkata'))
        >>> dateutils.to_date(unaware)
        datetime.date(2011, 8, 15)
        >>> dateutils.to_date(aware)
        datetime.date(2011, 8, 16)

    :param date_time:
    :param local_tz:
    :return:
    """
    if isinstance(date_time, datetime.datetime):
        if is_naive(date_time):
            raise ValidationException(
                description="Received naive datetime object",
            )
        else:
            if not local_tz:
                local_tz = tzlocal
            return date_time.astimezone(local_tz).date()
    else:
        return date_time


def to_time(date_time):
    """
    Converts the datetime object into date object in local timezone.
    Fails if the datetime in naive.

    Examples:
        >>> aware = datetime.datetime(2011, 8, 15, 18, 40, 0, 0, pytz.UTC)
        >>> unaware = datetime.datetime(2011, 8, 15, 18, 40, 0, 0)   # This is considered as UTC
        >>> dateutils.to_time(aware)
        datetime.time(0, 10)
        >>> aware = datetime.datetime(2011, 8, 15, 18, 40, 0, 0, pytz.timezone('Asia/Kolkata'))
        >>> dateutils.to_time(aware)
        datetime.time(18, 40)

    :param date_time:
    :return:
    """
    if isinstance(date_time, datetime.datetime):
        if is_naive(date_time):
            raise ValidationException(
                description="Received naive datetime object",
            )
        else:
            return date_time.astimezone(tzlocal).time()
    elif isinstance(date_time, datetime.date):
        return datetime.time.min
    elif isinstance(date_time, datetime.time):
        return date_time


def current_date():
    return to_date(current_datetime())


def current_time():
    return to_time(current_datetime())


def subtract(date_, days):
    return date_ - timedelta(days=days)


def add(date_, days):
    return date_ + timedelta(days=days)


def date_to_ymd_str(date_time):
    if isinstance(date_time, datetime.datetime):
        if is_naive(date_time):
            raise ValidationException(
                description="Received naive datetime object",
            )
        return date_time.astimezone(tzlocal).strftime("%Y-%m-%d")
    else:
        return date_time.strftime("%Y-%m-%d")


def date_range_inclusive(start, end):
    return [start + timedelta(i) for i in range((end - start).days + 1)]


def date_range_start_inclusive(start, end):
    return [start + timedelta(i) for i in range((end - start).days)]


def date_range_exclusive(start, end):
    return [start + timedelta(i) for i in range(1, (end - start).days)]


def ymd_str_to_date(date_str):
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


def validate_time_format(time):
    return datetime.datetime.strptime(time, "%H:%M:%S")


def validate_date_format(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d").date()


def isoformat_datetime(date_):
    if isinstance(date_, datetime.datetime):
        return date_.replace(microsecond=0).isoformat()
    else:
        return date_.isoformat()


def isoformat_str_to_datetime(isoformat_str):
    # NOTE: Using dateutil.parser here, because datetime.strptime doesn't have any directive to parse
    # timezone part of ISO Format datetime string using RFC 3339, that is +05:30. strptime can parse "+0530" however.
    return dateutil.parser.parse(isoformat_str)


def is_same_date(date_time1, date_time2):
    return date_time1 and date_time2 and date_time1 == date_time2


def localize_datetime(datetime_val):
    if is_naive(datetime_val):
        return tzlocal.localize(datetime_val)
    else:
        return datetime_val.astimezone(tzlocal)


def datetime_to_utc(datetime_val):
    if is_naive(datetime_val):
        return tzutc.localize(datetime_val)
    else:
        return datetime_val.astimezone(tzutc)


def date_range(start_date, end_date, end_inclusive=False):
    """
    date range
    :param start_date:
    :param end_date:
    :param end_inclusive:
    :return:
    """
    if not end_inclusive:
        end_date = end_date - DELTA
    while start_date <= end_date:
        yield start_date
        start_date = start_date + DELTA


def datetime_at_midnight(date_time):
    """
    :param date_time:
    :return:
    """
    next_day_midnight = datetime.datetime.combine(
        to_date(date_time),
        datetime.time(),
    )
    next_day_midnight_with_timezone = localize_datetime(next_day_midnight)
    return next_day_midnight_with_timezone


def datetime_at_given_time(date_time, time):
    date_at_time = datetime.datetime.combine(to_date(date_time), time)
    date_at_time_with_timezone = localize_datetime(date_at_time)
    return date_at_time_with_timezone


def next_month_number(month_number):
    return month_number + 1 if month_number < 12 else 1


def get_settlement_date(current_time, next_month=False):
    # TODO Remove hard-coding of 2/mm/yyyy 15:00:00.000
    # Got this data from https://treebo.atlassian.net/browse/PROM-1428
    if next_month:
        return localize_datetime(
            datetime.datetime(
                year=current_time.year,
                month=next_month_number(
                    current_time.month,
                ),
                day=2,
                hour=15,
            ),
        )
    return localize_datetime(datetime.datetime(year=current_time.year, month=current_time.month, day=2, hour=15))


def today():
    return current_datetime()


def tomorrow():
    return today() + timedelta(days=1)


def yesterday():
    return today() - timedelta(days=1)


def today_plus_days(days):
    return today() + timedelta(days=days)


def today_minus_days(days):
    return today() - timedelta(days=days)


def every_one_hour_datetime_in_a_range(start_datetime, end_datetime):
    # get all the time ranges between start and end time

    # For Eg: s=9:30am & e=11:30AM - then return 9AM, 10AM, 11AM, 12AM
    start_datetime = datetime_to_utc(start_datetime).replace(minute=0, second=0, microsecond=0)
    end_datetime = datetime_to_utc(end_datetime).replace(minute=0, second=0, microsecond=0)

    date_times = [start_datetime]
    date_time = start_datetime

    while date_time < end_datetime:
        date_time += timedelta(hours=1)
        date_times.append(date_time.replace(minute=0, second=0, microsecond=0))

    return date_times


def every_date_in_a_range(start_date, end_date):
    # get all the time ranges between start and end time

    if end_date < start_date:
        return []

    dates = [start_date]
    date_entry = start_date

    while date_entry < end_date:
        date_entry += timedelta(days=1)
        dates.append(date_entry)
    return dates


def to_string_hr(obj):
    return localize_datetime(obj).strftime(datetime_format_hr)


def to_string(obj):
    return obj.strftime(datetime_format)


def date_to_string(obj):
    return obj.strftime(date_format)


def time_to_string(obj):
    return obj.strftime(time_format)


def from_string(obj):
    return datetime.datetime.strptime(obj, datetime_format)


def date_from_string(obj):
    return datetime.datetime.strptime(obj, date_format).date()


def parse_datetime(obj, should_localize=False):
    if not obj:
        return None
    ret_val = None
    if isinstance(obj, datetime.datetime):
        ret_val = obj
    elif isinstance(obj, str):
        ret_val = datetime.datetime.strptime(obj, datetime_format)
    else:
        raise ValueError("Invalid type {} of obj {} to parse datetime".format(obj, type(obj)))
    if should_localize:
        return localize_datetime(ret_val)
    return ret_val


def next_day_of_week(day_of_week):
    return next_day_of_week_map[day_of_week]


def get_financial_year(obj):
    month = obj.month
    return obj.year if (month - 3) > 0 else obj.year - 1


def month_datetime_range(month, year):
    month_start = datetime.datetime(month=month, year=year, day=1, tzinfo=local_timezone())
    next_month, next_year = (month + 1, year) if month < 12 else (1, year + 1)
    return month_start, datetime.datetime(month=next_month, year=next_year, day=1, tzinfo=local_timezone())


def get_day_of_week(datetime_val):
    day_num = datetime_val.weekday()
    days = [DayOfWeek.MONDAY, DayOfWeek.TUESDAY, DayOfWeek.WEDNESDAY, DayOfWeek.THURSDAY, DayOfWeek.FRIDAY,
            DayOfWeek.SATURDAY, DayOfWeek.SUNDAY]
    return days[day_num]


def parse_time(time_str):
    time.strptime(time_str, time_format)


def get_timezone_for_address(address):
    timezone_str = country_code_to_tz_map.get(address.country.code)
    if not timezone_str:
        return None
    return pytz.timezone(timezone_str)


def get_timezone_for_region(region_id):
    timezone_str = region_id_to_tz_map.get(region_id)
    if not timezone_str:
        return None
    return pytz.timezone(timezone_str)


def to_tz_of_address(datetime_val, address):
    timezone = get_timezone_for_address(address)
    if not timezone:
        raise ValidationException(message="Timezone not defined for address: {}".format(address))
    return datetime_val.astimezone(timezone)


def to_tz_of_region(datetime_val, region_id):
    timezone = get_timezone_for_region(region_id)
    if not timezone:
        raise ValidationException(message="Timezone not defined for region: {}".format(region_id))
    return datetime_val.astimezone(timezone)
