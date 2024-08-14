from marshmallow import fields
from marshmallow.decorators import post_load

from flaskd3.appcore.schema.base_schema import (
    BaseSchema,
    BitMaskValueObjectField,
    EnumField,
    ValueObjectSchema,
    VersionMixinSchema,
)
from flaskd3.types.base_enum import BaseEnum
from flaskd3.types.state_machine import StateTransition
from flaskd3.infrastructure.async_job_runner.constants import AsyncJobStatus
from flaskd3.common.constants import (
    DistanceUnit,
    MediaType,
    PlaceType,
    RelationshipStatus, RelationshipAction
)
from flaskd3.common.money.constants import CurrencyType
from flaskd3.common.money.money import Money
from flaskd3.common.utils.validators import (
    validate_empty_string,
    validate_phone_number,
)
from flaskd3.common.value_objects import (
    Address,
    DateTimeDuration,
    DaysOfWeek,
    Distance,
    DistanceInfo,
    DistanceWindow,
    GeoLocation,
    IDProof,
    IntRange,
    MediaInfo,
    Name,
    PhoneNumber,
    Place,
    TimeDuration,
    TimeDurationsInDays,
    RelationshipActionRequest, DateDuration
)


class ApiErrorSchema(BaseSchema):
    """
    API Error Schema
    """

    code = fields.String(
        required=True,
        attribute="code",
        description="The error code to identify the error uniquely",
    )
    message = fields.String(
        required=True,
        attribute="message",
        description="User visible string of the error",
    )
    developerMessage = fields.String(
        required=True,
        attribute="developer_message",
        description="A more descriptive error message for developers",
    )
    extraPayload = fields.Dict(
        required=False,
        attribute="extra_payload",
        description="Additional Information to be passed for debugging",
    )
    requestId = fields.String(attribute="request_id", description="The request id of the call.")


class PhoneSchema(ValueObjectSchema):
    """
    Phone schema
    """

    countryCode = fields.String(allow_none=True, attribute="country_code", validate=validate_empty_string)
    number = fields.String(required=True, validate=[validate_empty_string, validate_phone_number])

    @property
    def value_object_class(self):
        return PhoneNumber


class NameSchema(ValueObjectSchema):
    """
    Name Schema
    """

    @property
    def value_object_class(self):
        return Name

    salutation = fields.String(allow_none=True, attribute="salutation")
    firstName = fields.String(allow_none=True, attribute="first_name")
    middleName = fields.String(allow_none=True, attribute="middle_name")
    lastName = fields.String(allow_none=True, attribute="last_name")


class DistanceSchema(ValueObjectSchema):
    """
    Distance Schema
    """

    value = fields.Float(attribute="value")
    unit = EnumField(DistanceUnit)

    @property
    def value_object_class(self):
        return Distance


class DistanceWindowSchema(ValueObjectSchema):
    """
    Distance Window Schema
    """

    startDistance = fields.Nested(DistanceSchema, attribute="start_distance", allow_none=True)
    endDistance = fields.Nested(DistanceSchema, attribute="end_distance", allow_none=True)

    @property
    def value_object_class(self):
        return DistanceWindow


class PlaceSchema(ValueObjectSchema):
    """
    Place Schema
    """

    placeType = EnumField(PlaceType, attribute="place_type")
    name = fields.String(attribute="name")
    code = fields.String(attribute="code")

    @property
    def value_object_class(self):
        return Place


class GeoLocationSchema(ValueObjectSchema):
    """
    Geo Location
    """

    latitude = fields.String(allow_none=False)
    longitude = fields.String(allow_none=False)

    @property
    def value_object_class(self):
        return GeoLocation


class AddressSchema(ValueObjectSchema):
    """
    Address schema
    """

    field1 = fields.String(allow_none=True, attribute="field_1", validate=validate_empty_string)
    field2 = fields.String(allow_none=True, attribute="field_2", validate=validate_empty_string)
    city = fields.Nested(PlaceSchema, allow_none=True)
    state = fields.Nested(PlaceSchema, allow_none=True)
    country = fields.Nested(PlaceSchema, allow_none=True)
    pincode = fields.String(allow_none=True, validate=validate_empty_string)
    geoLocation = fields.Nested(GeoLocationSchema, attribute="geo_location")

    @property
    def value_object_class(self):
        return Address


class TimeDurationSchema(ValueObjectSchema):
    """
    Working Hours schema
    """

    fromTime = fields.Time(required=True, attribute="from_time")
    toTime = fields.Time(required=True, attribute="to_time")

    @property
    def value_object_class(self):
        return TimeDuration


class DistanceInfoSchema(ValueObjectSchema):
    """
    Distance Info Schema
    """

    distanceText = fields.String(required=True)
    distanceValue = fields.Integer(required=True)
    durationText = fields.String(required=True)
    durationValue = fields.Integer(required=True)

    @property
    def value_object_class(self):
        return DistanceInfo


class TimeDurationsInDaysSchema(ValueObjectSchema):
    """
    Time durations in days of week schema
    """

    timeDurations = fields.Nested(TimeDurationSchema, attribute="time_durations", many=True)
    daysOfWeek = BitMaskValueObjectField(DaysOfWeek, attribute="days_of_week", required=True)

    @property
    def value_object_class(self):
        return TimeDurationsInDays


class DateTimeDurationSchema(ValueObjectSchema):

    fromDatetime = fields.DateTime(attribute="from_datetime", required=False)
    toDatetime = fields.DateTime(attribute="to_datetime", required=False)

    @property
    def value_object_class(self):
        return DateTimeDuration


class DateDurationSchema(ValueObjectSchema):

    fromDate = fields.Date(attribute="from_date", required=False)
    toDate = fields.Date(attribute="to_date", required=False)

    @property
    def value_object_class(self):
        return DateDuration


class MediaInfoSchema(ValueObjectSchema):

    mediaId = fields.String(description="media file path", attribute="media_id")
    info = fields.Dict(description="Media custom info", attribute="info")
    path = fields.String(description="media file path", attribute="path")
    mediaType = EnumField(MediaType, description="Media Type", attribute="media_type")
    description = fields.String(description="description", attribute="description")
    fileType = fields.String(description="The file type", attribute="file_type", required=True)

    @property
    def value_object_class(self):
        return MediaInfo


class MoneySchema(BaseSchema):

    amount = fields.Decimal(required=True, attribute="amount")
    currency = EnumField(CurrencyType, attribute="currency")

    @post_load()
    def load(self, data, **kwargs):
        return Money(data.get("amount"), data.get("currency", data.get("currency_type")))


class StateTransitionSchema(ValueObjectSchema):

    trigger = EnumField(BaseEnum, attribute="trigger")
    source = EnumField(BaseEnum, attribute="source", many=True)
    destination = EnumField(BaseEnum, attribute="destination")
    authorisedUserRoles = fields.List(fields.String, attribute="authorised_user_roles", many=True)

    @classmethod
    def value_object_class(cls):
        return StateTransition


class TransitionsMixinSchema(object):
    transitions = fields.Nested(StateTransitionSchema, attribute="transitions", many=True)


class IntRangeSchema(ValueObjectSchema):
    """
    Schema for int range
    """
    min = fields.Integer(allow_none=True, attribute="min")
    max = fields.Integer(allow_none=True, attribute="max")

    @property
    def value_object_class(self):
        return IntRange


class JobSchema(BaseSchema, VersionMixinSchema):

    jobId = fields.String(attribute="job_id")
    data = fields.Dict(attribute="data", required=False)
    runTime = fields.DateTime(attribute="run_time", required=False)
    jobName = fields.String(attribute="job_name", required=False)
    status = EnumField(AsyncJobStatus, attribute="status")
    response = fields.String(attribute="response", required=False)
    tries = fields.Integer(attribute="tries", required=False)


class RelationshipSchema(BaseSchema):
    relationshipId = fields.String(attribute="relationship_id")
    status = EnumField(RelationshipStatus, attribute="status")


class RelationshipActionRequestSchema(ValueObjectSchema):
    action = EnumField(RelationshipAction, attribute="action")
    actionDatetime = fields.DateTime(attribute="action_datetime")

    @property
    def value_object_class(self):
        return RelationshipActionRequest
