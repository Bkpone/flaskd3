import re
from datetime import datetime, time, date
from decimal import Decimal

from flaskd3.types.base_enum import BaseEnum
from flaskd3.types.mutable_value_object import MutableValueObject
from flaskd3.types.type_info import ValueObjectField
from flaskd3.types.value_object import BitMaskValueObject, ValueObject
from flaskd3.common.constants import (
    DayOfWeek,
    DistanceUnit,
    MediaType,
    PlaceType,
    RelationshipAction
)
from flaskd3.common.exceptions import ValidationException
from flaskd3.common.utils.dateutils import from_string, to_string, to_string_hr, date_to_string


class AppInformation(ValueObject):
    app_name = ValueObjectField(str)


class JobData(ValueObject):
    job_id = ValueObjectField(str)
    job_name = ValueObjectField(str)
    run_time = ValueObjectField(datetime)
    data = ValueObjectField(dict, allow_none=True, default=None)


class Name(ValueObject):

    salutation = ValueObjectField(str, required=False)
    first_name = ValueObjectField(str, required=False)
    middle_name = ValueObjectField(str, required=False)
    last_name = ValueObjectField(str, required=False)

    @property
    def full_name(self):
        return "".join(
            [
                "{} ".format(self.salutation or ""),
                "{}".format(self.first_name) if self.first_name else "",
                " {}".format(self.middle_name) if self.middle_name else "",
                " {}".format(self.last_name) if self.last_name else "",
            ]
        )

    def dict(self):
        return {
            "salutation": self.salutation.value if self.salutation else None,
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "last_name": self.last_name,
        }

    def __str__(self):
        return str(self.full_name)


class PhoneNumber(ValueObject):
    """
    Phone number with country code
    """

    _allowed_phone_regex = ["\d{9,10}$", "^\+\d{0,3}\-\d{9,10}$"]

    def __init__(self, number, country_code):
        """
        :param str number:
        :param str country_code:
        """
        self.number = number
        self.country_code = country_code if country_code[0] == "+" else "+" + country_code
        if not PhoneNumber.validate(self):
            raise ValidationException(
                "Phone number needs to be in the format +( 1-3 digit country code )-( 9-10 digit number )")

    def dict(self):
        if self.country_code:
            return "{}-{}".format(self.country_code, self.number)
        return str(self.number)

    @staticmethod
    def from_dict(data):
        if isinstance(data, dict):
            return PhoneNumber(country_code=data["country_code"], number=data["number"])
        number_list = data.split("-")
        number_list_len = len(number_list)
        if number_list_len > 2:
            raise ValidationException("Phone number cannot have more that two sections")
        if number_list_len == 2:
            return PhoneNumber(country_code=number_list[0], number=number_list[1])
        if number_list_len == 1:
            raise ValidationException(
                "Phone number needs to be in the format +( 3 digit country code )-( 9-10 digit number )")
        return None

    def __eq__(self, other):
        if not other:
            return False
        if isinstance(other, str):
            other = PhoneNumber.from_dict(other)
        if not isinstance(other, PhoneNumber):
            raise ValueError("Value should be of type Phone number or string for Phone number compare.")
        if other.country_code and self.country_code:
            if other.country_code != self.country_code:
                return False
        return other.number == self.number

    def __str__(self):
        return self.dict()

    @property
    def full_number(self):
        return "{}{}".format(self.country_code, self.number) if self.country_code else str(self.number)

    @property
    def e_164(self):
        return "{}{}".format(self.country_code, self.number.replace(" ", "").replace("-", "")[-10:])

    @classmethod
    def validate(cls, phone_number):
        if isinstance(phone_number, cls):
            phone_number = str(phone_number)
        for reg_ex in cls._allowed_phone_regex:
            if re.search(reg_ex, phone_number):
                return True
        return False


class IDProof(ValueObject):
    def __init__(self, id_proof_type, id_number, id_kyc_url, id_proof_country_code):
        """

        :param ths_common.constants.booking_constants.IDProofType id_proof_type:
        :param str id_number:
        :param str id_kyc_url:
        :param str id_proof_country_code:
        """
        self.id_proof_type = id_proof_type
        self.id_number = id_number
        self.id_kyc_url = id_kyc_url
        self.id_proof_country_code = id_proof_country_code

    def dict(self):
        return {
            "id_proof_type": self.id_proof_type,
            "id_number": self.id_number,
            "id_kyc_url": self.id_kyc_url,
            "id_proof_country_code": self.id_proof_country_code,
        }

    @staticmethod
    def from_dict(json):
        return IDProof(
            id_proof_type=json.get("id_proof_type"),
            id_number=json.get("id_number"),
            id_kyc_url=json.get("id_kyc_url"),
            id_proof_country_code=json.get("id_proof_country_code"),
        )


class Place(ValueObject):
    """
    Place value object
    """
    place_type = ValueObjectField(PlaceType)
    code = ValueObjectField(str)
    name = ValueObjectField(str)

    def __eq__(self, __o: object) -> bool:
        if not __o:
            return False
        if not isinstance(__o, Place):
            raise ValidationException(description="Can only compare Place type with Place.")
        return self.place_type == __o.place_type and self.code == __o.code and self.name == __o.name


class Address(ValueObject):
    """
    An Address value object
    """

    def __init__(self, field_1, field_2, city, state, country, pincode, geo_location=None):
        """

        :param str field_1:
        :param str field_2:
        :param place city:
        :param place state:
        :param place country:
        :param str pincode:
        """
        self.field_1 = field_1
        self.field_2 = field_2
        self.city = city if isinstance(city, Place) else Place.from_dict(city)
        self.state = state if isinstance(state, Place) else Place.from_dict(state)
        self.country = country if isinstance(country, Place) else Place.from_dict(country)
        self.pincode = pincode
        self.geo_location = geo_location if isinstance(
            geo_location, GeoLocation) else GeoLocation.from_dict(geo_location)

    @staticmethod
    def from_dict(dict_obj):
        return Address(
            field_1=dict_obj.get("field_1"),
            field_2=dict_obj.get("field_2"),
            city=dict_obj.get("city"),
            state=dict_obj.get("state"),
            country=dict_obj.get("country"),
            pincode=dict_obj.get("pincode"),
            geo_location=dict_obj.get("geo_location"),
        )

    @property
    def address(self):
        return "".join(
            [
                "{},".format(self.field_1 or ""),
                " {},".format(self.field_2) if self.field_1 else "",
                "city: {},".format(self.city) if self.city.name else "",
                "state: {},".format(self.state) if self.state.name else "",
                "country: {},".format(self.country) if self.country.name else "",
                "pincode: {}".format(self.pincode) if self.pincode else "",
            ]
        )

    def __str__(self):
        return self.address

    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, Address):
            raise ValidationException(description="Can only compare equality between Addresses of same type")
        return (
            self.field_1 == other.field_1
            and self.field_2 == other.field_2
            and self.city == other.city
            and self.state == other.state
            and self.country == other.country
            and self.pincode == other.pincode
            and self.geo_location == other.geo_location
        )


class DateDuration(ValueObject):
    """
    Date duration
    """

    date_format = "%Y-%m-%d"

    from_date = ValueObjectField(date, allow_none=True)
    to_date = ValueObjectField(date, allow_none=True)

    def init(self, **kwargs):
        if self.from_date and self.to_date and self.to_date < self.from_date:
            raise ValueError("Invalid date duration (to should be greater than from)")

    def __contains__(self, item):
        if not isinstance(item, date):
            item = from_string(item)
        res1 = res2 = True
        if self.from_date:
            res1 = self.from_date <= item
        if self.to_date:
            res2 = item <= self.to_date
        return res1 and res2

    def overlap(self, other):
        if (not self.from_date and not other.from_date) or (not self.to_date and not other.to_date):
            return True

        if not self.from_date:
            return other.from_date <= self.to_date

        if not other.from_datetime:
            return self.from_date <= other.to_date

        if not self.to_date:
            return other.to_date >= self.from_date

        if not other.to_datetime:
            return self.to_date >= other.from_date

        return (self.from_date <= other.from_date <= self.to_date) or (self.from_date <= other.to_date <= self.to_date)

    def contains(self, other):
        if other.from_date in self and other.to_date in self:
            return True
        return False

    def merge(self, other):
        if (not self.from_date and not other.from_date) or (not self.to_date and not other.to_date):
            from_date = None
            to_date = None
        elif not self.from_date or not other.from_date:
            from_date = None
            to_date = other.to_date if other.to_date >= self.to_date else self.to_date
        elif not self.to_date or not other.to_date:
            to_date = None
            from_date = other.from_date if other.from_date <= self.from_date else self.from_date
        else:
            to_date = other.to_date if other.to_date >= self.to_date else self.to_date
            from_date = other.from_date if other.from_date <= self.from_date else self.from_date
        return DateDuration(from_date=from_date, to_date=to_date)

    def dict(self):
        return {
            "from_date": date_to_string(self.from_date),
            "to_date": date_to_string(self.to_date),
        }

    def __str__(self):
        return "{} - {}".format(to_string_hr(self.from_date), to_string_hr(self.to_date))

    @classmethod
    def from_dict(cls, json: dict):
        from_date = json.get("from_date")
        from_date = datetime.strptime(from_date, cls.date_format) if not isinstance(
            from_date, date) else from_date
        to_date = json.get("to_date")
        to_date = datetime.strptime(to_date, cls.date_format) if not isinstance(
            to_date, date) else to_date
        return cls(from_date=from_date, to_date=to_date)


class DateTimeDuration(ValueObject):
    """
    Datetime duration
    """

    datetime_format = "%Y-%m-%dT%H:%M:%S%z"

    from_datetime = ValueObjectField(datetime, allow_none=True)
    to_datetime = ValueObjectField(datetime, allow_none=True)

    def init(self, **kwargs):
        if self.from_datetime and self.to_datetime and self.to_datetime < self.from_datetime:
            raise ValueError("Invalid time duration (to should be greater than from)")

    def __contains__(self, item):
        if not isinstance(item, datetime):
            item = from_string(item)
        res1 = res2 = True
        if self.from_datetime:
            res1 = self.from_datetime <= item
        if self.to_datetime:
            res2 = item <= self.to_datetime
        return res1 and res2

    def overlap(self, other):
        if (not self.from_datetime and not other.from_datetime) or (not self.to_datetime and not other.to_datetime):
            return True

        if not self.from_datetime:
            return other.from_datetime <= self.to_datetime

        if not other.from_datetime:
            return self.from_datetime <= other.to_datetime

        if not self.to_datetime:
            return other.to_datetime >= self.from_datetime

        if not other.to_datetime:
            return self.to_datetime >= other.from_datetime

        return (self.from_datetime <= other.from_datetime <= self.to_datetime) or (self.from_datetime <= other.to_datetime <= self.to_datetime)

    def contains(self, other):
        if other.from_datetime in self and other.to_datetime in self:
            return True
        return False

    def merge(self, other):
        if (not self.from_datetime and not other.from_datetime) or (not self.to_datetime and not other.to_datetime):
            from_datetime = None
            to_datetime = None
        elif not self.from_datetime or not other.from_datetime:
            from_datetime = None
            to_datetime = other.to_datetime if other.to_datetime >= self.to_datetime else self.to_datetime
        elif not self.to_datetime or not other.to_datetime:
            to_datetime = None
            from_datetime = other.from_datetime if other.from_datetime <= self.from_datetime else self.from_datetime
        else:
            to_datetime = other.to_datetime if other.to_datetime >= self.to_datetime else self.to_datetime
            from_datetime = other.from_datetime if other.from_datetime <= self.from_datetime else self.from_datetime
        return DateTimeDuration(from_datetime=from_datetime, to_datetime=to_datetime)

    def dict(self):
        return {
            "from_datetime": to_string(self.from_datetime),
            "to_datetime": to_string(self.to_datetime),
        }

    def __str__(self):
        return "{} - {}".format(to_string_hr(self.from_datetime), to_string_hr(self.to_datetime))

    @classmethod
    def from_dict(cls, json: dict):
        from_datetime = json.get("from_datetime")
        from_datetime = datetime.strptime(from_datetime, cls.datetime_format) if not isinstance(
            from_datetime, datetime) else from_datetime
        to_datetime = json.get("to_datetime")
        to_datetime = datetime.strptime(to_datetime, cls.datetime_format) if not isinstance(
            to_datetime, datetime) else to_datetime
        return cls(from_datetime=from_datetime, to_datetime=to_datetime)


class TimeDuration(ValueObject):
    """
    Time duration
    """

    time_format = "%H:%M:%S"

    def __init__(self, from_time: time, to_time: time):
        """
        :param str from_time:
        :param str to_time:
        """
        if from_time and to_time and to_time <= from_time:
            raise ValueError("Invalid time duration (to should be greater than from")
        self.from_time = from_time
        self.to_time = to_time

    def __contains__(self, item):
        if isinstance(item, datetime):
            item = item.time()
        return self.from_time <= item <= self.to_time

    def overlap(self, other):
        if (not self.from_time and not other.from_time) or (not self.to_time and not other.to_time):
            return True

        if not self.from_time:
            return other.from_time <= self.to_time

        if not other.from_time:
            return self.from_time <= other.to_time

        if not self.to_time:
            return other.to_time >= self.from_time

        if not other.to_time:
            return self.to_time >= other.from_time

        return (self.from_time <= other.from_time <= self.to_time) or (self.from_time <= other.to_time <= self.to_time)

    def dict(self):
        return {
            "from_time": self.from_time.strftime(self.time_format),
            "to_time": self.to_time.strftime(self.time_format),
        }

    def __str__(self):
        return "{} - {}".format(
            self.from_time.strftime(self.time_format),
            self.to_time.strftime(self.time_format),
        )

    @classmethod
    def from_dict(cls, json: dict):
        from_time = json.get("from_time")
        from_time = datetime.strptime(from_time, cls.time_format).time(
        ) if not isinstance(from_time, time) else from_time
        to_time = json.get("to_time")
        to_time = datetime.strptime(to_time, cls.time_format).time() if not isinstance(to_time, time) else to_time
        return cls(from_time=from_time, to_time=to_time)


class TimeDurationsInDays(ValueObject):
    def __init__(self, time_durations, days_of_week):
        self.time_durations = []
        for entry1 in time_durations:
            for entry2 in self.time_durations:
                if entry2.overlap(entry1):
                    raise ValueError("The time duration {} overlaps {}".format(entry1, entry2))
            self.time_durations.append(entry1)
        self.days_of_week = days_of_week

    def overlap(self, other):
        if not self.days_of_week.overlap(other.days_of_week):
            return False
        for entry1 in self.time_durations:
            for entry2 in other.time_durations:
                if entry2.overlap(entry1):
                    return True

    def __contains__(self, day_time_tuple):
        if not isinstance(day_time_tuple, tuple) or len(day_time_tuple) != 2:
            raise ValueError("Invalid item should be tuple (day, time).")
        if day_time_tuple[0] not in self.days_of_week:
            return False
        for entry in self.time_durations:
            if day_time_tuple[1] in entry:
                return True
        return False

    def dict(self):
        return dict(
            time_durations=[entry.dict() for entry in self.time_durations],
            days_of_week=self.days_of_week.dict(),
        )

    @classmethod
    def from_dict(cls, json: dict):
        time_durations = []
        for time_duration in json["time_durations"]:
            if not isinstance(time_duration, TimeDuration):
                time_duration = TimeDuration.from_dict(time_duration)
            time_durations.append(time_duration)
        days_of_week = json["days_of_week"]
        if not isinstance(days_of_week, DaysOfWeek):
            days_of_week = DaysOfWeek.from_dict(days_of_week)
        return cls(time_durations, days_of_week)


class GeoPoint(ValueObject):
    x = ValueObjectField(int)
    y = ValueObjectField(int)

    def get_geo_node_id(self):
        return str(self.x * 10000 + self.y)


class GeoLocation(ValueObject):
    longitude = ValueObjectField(str)
    latitude = ValueObjectField(str)

    LON_MAX = 180
    LON_MIN = -180
    LAT_MAX = 85
    LAT_MIN = -85

    @property
    def latitude_float(self):
        return float(self.latitude)

    @property
    def longitude_float(self):
        return float(self.longitude)

    @property
    def latitude_normalized(self):
        val_minutes = float(self.latitude) * 60
        return self.LAT_MAX*60 - int(val_minutes)

    @property
    def longitude_normalized(self):
        val_minutes = float(self.longitude) * 60
        return int(val_minutes) - self.LON_MIN * 60

    def get_normalized_point(self):
        return GeoPoint(x=self.longitude_normalized, y=self.latitude_normalized)

    def get_geo_node_id(self):
        return str(self.longitude_normalized * 10000 + self.longitude_normalized)

    def init(self, **kwargs):
        try:
            latitude_float = self.latitude_float
            longitude_float = self.longitude_float
        except ValueError:
            raise ValidationException("Invalid geo location: {}:{}".format(self.latitude, self.longitude))
        if not (GeoLocation.LAT_MIN <= latitude_float <= GeoLocation.LAT_MAX and GeoLocation.LON_MIN <= longitude_float <= GeoLocation.LON_MAX):
            raise ValidationException(
                "Invalid geo location out of valid range: {}:{}".format(self.latitude, self.longitude))

    @classmethod
    def from_normalized_point(cls, geo_point):
        latitude = "{:.8f}".format((cls.LAT_MAX * 60 - geo_point.y)/60)
        longitude = "{:.8f}".format((geo_point.x + cls.LON_MIN * 60)/60)
        return cls(latitude=latitude, longitude=longitude)

    def dict(self):
        return {"latitude": self.latitude, "longitude": self.longitude}

    def __eq__(self, __o: object) -> bool:
        if not __o:
            return False
        if not isinstance(__o, GeoLocation):
            raise ValidationException(description="Cannot compare two different types.")
        return self.longitude == __o.longitude and self.latitude == __o.latitude


class GeoBoundingBox(ValueObject):
    top_left = ValueObjectField(GeoLocation)
    top_right = ValueObjectField(GeoLocation)
    bottom_left = ValueObjectField(GeoLocation)
    bottom_right = ValueObjectField(GeoLocation)


class DaysOfWeek(BitMaskValueObject):
    enum_class = DayOfWeek


class DistanceInfo(ValueObject):
    def __init__(self, distance_text, distance_value, duration_text, duration_value):
        self.distance_text = distance_text
        self.distance_value = distance_value
        self.duration_text = duration_text
        self.duration_value = duration_value


class Distance(ValueObject):
    def __init__(self, value, unit):
        self.value = value
        self.unit = unit if isinstance(unit, DistanceUnit) else DistanceUnit(unit)

    @property
    def in_metres(self):
        unit = self.unit
        if unit == DistanceUnit.METER:
            return self.value
        elif unit == DistanceUnit.KILOMETER:
            return self.value * 1000
        elif unit == DistanceUnit.MILE:
            return self.value * 1609.34
        elif unit == DistanceUnit.FEET:
            return self.value * 0.3048

    def __eq__(self, other):
        return self.in_metres == other.in_metres

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.in_metres < other.in_metres

    def __gt__(self, other):
        return self.in_metres > other.in_metres

    def __le__(self, other):
        return self.in_metres < other.in_metres or self.in_metres == other.in_metres

    def __ge__(self, other):
        return self.in_metres > other.in_metres or self.in_metres == other.in_metres

    @staticmethod
    def from_dict(dict_obj):
        return Distance(dict_obj["value"], DistanceUnit(dict_obj["unit"]))


class DistanceWindow(ValueObject):
    start_distance = ValueObjectField(Distance, allow_none=True)
    end_distance = ValueObjectField(Distance, allow_none=True)

    def __init__(self, start_distance: Distance, end_distance: Distance):
        if start_distance and end_distance and end_distance <= start_distance:
            raise ValueError("Invalid DistanceWindow (end should be greater than start)")
        self.start_distance = start_distance
        self.end_distance = end_distance

    def __contains__(self, distance):
        distance = distance if isinstance(distance, Distance) else Distance(distance)
        op1 = op2 = True
        if self.start_distance:
            op1 = distance >= self.start_distance
        if self.end_distance:
            op2 = distance <= self.end_distance
        return op1 and op2

    def overlap(self, other):
        if (not self.start_distance and not other.start_distance) or (not self.end_distance and not other.end_distance):
            return True
        if not self.start_distance:
            return other.start_distance <= self.end_distance
        if not other.start_distance:
            return self.start_distance <= other.end_distance
        if not self.end_distance:
            return other.end_distance >= self.start_distance
        if not other.end_distance:
            return self.end_distance >= other.start_distance
        return (self.start_distance <= other.start_distance <= self.end_distance) or (self.start_distance <= other.end_distance <= self.end_distance)

    @staticmethod
    def from_dict(dict_obj):
        start_distance = dict_obj.get("start_distance")
        start_distance = Distance.from_dict(start_distance) if isinstance(start_distance, dict) else start_distance
        end_distance = dict_obj.get("end_distance")
        end_distance = Distance.from_dict(end_distance) if isinstance(end_distance, dict) else end_distance
        return DistanceWindow(start_distance, end_distance)


class MediaInfo(ValueObject):
    info = ValueObjectField(dict, required=False)
    path = ValueObjectField(str)
    media_id = ValueObjectField(str)
    media_type = ValueObjectField(MediaType)
    description = ValueObjectField(str, required=False)
    file_type = ValueObjectField(str)


class ActionLog(ValueObject):
    action_request = ValueObjectField(dict)
    old_state = ValueObjectField(str)
    new_state = ValueObjectField(str)


class ActionRequest(ValueObject):
    action = ValueObjectField(BaseEnum)
    action_datetime = ValueObjectField(datetime)
    payload = ValueObjectField(dict)


class EntityInfo(ValueObject):
    entity_type = ValueObjectField(str)
    entity_id = ValueObjectField(str)


class IntRange(ValueObject):
    min = ValueObjectField(int, allow_none=True)
    max = ValueObjectField(int, allow_none=True)

    @staticmethod
    def from_dict(dict_obj):
        return IntRange(min=dict_obj.get("min"), max=dict_obj.get("max"))

    def __contains__(self, item):
        if not item:
            return False
        if self.min:
            if item < self.min:
                return False
        if self.max:
            if item > self.max:
                return False
        return True

    def __str__(self):
        return "{} to {}".format(self.min if self.min else "No Bound", self.max if self.max else "No Bound")


class RelationshipActionRequest(ValueObject):

    action = ValueObjectField(RelationshipAction)
    action_datetime = ValueObjectField(datetime)



