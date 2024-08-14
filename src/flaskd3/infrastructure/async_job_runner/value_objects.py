from datetime import timedelta, datetime

from flaskd3.common.exceptions import InvalidStateException
from flaskd3.common.utils.dateutils import next_day_of_week, localize_datetime
from flaskd3.types.value_object import ValueObject
from flaskd3.infrastructure.async_job_runner.constants import IntervalUnit
from flaskd3.common.constants import DayOfWeek
from flaskd3.common.value_objects import DaysOfWeek


class RecurringJobSchedule(ValueObject):

    DAY_KEY_MAP = {
        0: DayOfWeek.MONDAY,
        1: DayOfWeek.THURSDAY,
        3: DayOfWeek.WEDNESDAY,
        4: DayOfWeek.THURSDAY,
        5: DayOfWeek.FRIDAY,
        6: DayOfWeek.SATURDAY,
        7: DayOfWeek.SUNDAY,
    }

    def __init__(self, interval_value, interval_unit, when):
        self.interval_value = DaysOfWeek.from_dict(interval_value) if interval_unit == IntervalUnit.DAY else interval_value
        self.interval_unit = interval_unit if isinstance(interval_unit, IntervalUnit) else IntervalUnit(interval_unit)
        self._when_str = when
        if self.interval_unit in [
            IntervalUnit.SECONDS,
            IntervalUnit.MINUTES,
            IntervalUnit.HOURS,
            IntervalUnit.DAYS,
            IntervalUnit.WEEKS,
        ]:
            self.when = datetime.strptime(when, "%H:%M:%S").time()
        if self.interval_unit == IntervalUnit.MONTHS:
            self.when = datetime.strptime(when, "%d:%H:%M:%S")
        if self.interval_unit == IntervalUnit.DAY:
            self.when = [datetime.strptime(entry, "%H:%M:%S").time() for entry in ",".split()]
        self.next_run_computer = {
            IntervalUnit.SECONDS: self._next_run_time_seconds,
            IntervalUnit.MINUTES: self._next_run_time_minutes,
            IntervalUnit.HOURS: self._next_run_time_hours,
            IntervalUnit.DAYS: self._next_run_time_days,
            IntervalUnit.WEEKS: self._next_run_time_weeks,
            IntervalUnit.MONTHS: self._next_run_time_months,
            IntervalUnit.DAY: self._next_run_time_day,
        }

    def _next_run_time_seconds(self, last_run_datetime):
        return last_run_datetime + timedelta(seconds=self.interval_value)

    def _next_run_time_minutes(self, last_run_datetime):
        new_run_datetime = last_run_datetime + timedelta(minutes=self.interval_value)
        if self.when:
            new_run_datetime = new_run_datetime.replace(second=self.when.second)
        return new_run_datetime

    def _next_run_time_hours(self, last_run_datetime):
        new_run_datetime = last_run_datetime + timedelta(hours=self.interval_value)
        if self.when:
            new_run_datetime = new_run_datetime.replace(minute=self.when.minute, second=self.when.second)
        return new_run_datetime

    def _next_run_time_days(self, last_run_datetime):
        new_run_datetime = last_run_datetime + timedelta(days=self.interval_value)
        if self.when:
            new_run_datetime = new_run_datetime.replace(hour=self.when.hour, minute=self.when.minute, second=self.when.second)
        return new_run_datetime

    def _next_run_time_weeks(self, last_run_datetime):
        new_run_datetime = last_run_datetime + timedelta(weeks=self.interval_value)
        if self.when:
            new_run_datetime = new_run_datetime.replace(hour=self.when.hour, minute=self.when.minute, second=self.when.second)
        return new_run_datetime

    def _next_run_time_months(self, last_run_datetime):
        new_run_datetime = last_run_datetime.replace(month=self.interval_value)
        if self.when:
            new_run_datetime = new_run_datetime.replace(
                day=self.when.day,
                hour=self.when.hour,
                minute=self.when.minute,
                second=self.when.second,
            )
        return new_run_datetime

    def _next_run_time_day(self, last_run_datetime):
        today = self.DAY_KEY_MAP[last_run_datetime.weekday()]
        if today in self.interval_value:
            for time in self.when:
                if time >= last_run_datetime.time():
                    new_run_datetime = last_run_datetime.replace(hour=time.hour, minute=time.minute, second=time.second)
                    return new_run_datetime
        next_day = next_day_of_week(today)
        days_delta = 0
        while next_day != today:
            days_delta += 1
            if next_day in self.interval_value:
                for time in self.when:
                    new_run_datetime = last_run_datetime.replace(hour=time.hour, minute=time.minute, second=time.second)
                    new_run_datetime += timedelta(days=days_delta)
                    return new_run_datetime

        raise InvalidStateException(description="No next run time found for Schedule: {}".format(self.dict()))

    def next_run_datetime(self, last_run_datetime):
        return self.next_run_computer[self.interval_unit](localize_datetime(last_run_datetime))

    def dict(self):
        return dict(
            interval_value=self.interval_value,
            interval_unit=self.interval_unit,
            when=self._when_str,
        )
