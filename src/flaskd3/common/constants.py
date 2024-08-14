from flaskd3.types.base_enum import BaseEnum

SUPER_ADMIN_ROLE_ID = "super"
SYSTEM_ROLE_ID = "SYSTEM"
SUPER_ORG_ID = "SUP"
NOT_NONE = "NOT_NONE"


class ApplicationEnv(BaseEnum):
    LOCAL = "local", "Local"
    STAGE = "stage", "Staging"
    PROD = "prod", "Production"
    TEST = "testing", "Testing"


class Salutation(BaseEnum):
    """
    Salutations
    """

    MR = "mr", "Mr."
    MISS = "miss", "Miss."
    MS = "ms", "Ms."
    MRS = "mrs", "Mrs."
    MX = "mx", "Mx."
    DR = "dr", "Dr."
    SIR = "sir", "Sir."


class ContactType(BaseEnum):
    """
    Contact type
    """

    MOBILE_PHONE = "mobile_phone", "Mobile Phone"
    LANDLINE = "landline", "Landline"
    EMAIL = "email", "EMail"


class TaxTypes(BaseEnum):
    """
    Tax types
    """

    CGST = "cgst", "Central GST"
    SGST = "sgst", "State GST"
    IGST = "igst", "Integrated GST"
    VAT = "vat", "Value-Added Tax"


class ItemCodeTypes(BaseEnum):
    """
    The type of item code
    """

    HSN = "HSN"
    SAC = "SAC"


class ObjectTypes(object):
    """
    The object types
    """

    ENTITY = "entity"
    VALUE_OBJECT = "value_object"
    ENUM = "enum"
    BASIC_DATA = "basic_data"


class Gender(BaseEnum):
    """
    Gender types
    """

    MALE = "male", "Male"
    FEMALE = "female", "Female"
    TRANSGENDER = "transgender", "Transgender"


class DayOfWeek(BaseEnum):
    """
    Days of week
    """

    MONDAY = "monday", "Monday", 1
    TUESDAY = "tuesday", "Tuesday", 2
    WEDNESDAY = "wednesday", "Wednesday", 4
    THURSDAY = "thursday", "Thursday", 8
    FRIDAY = "friday", "Friday", 16
    SATURDAY = "saturday", "Saturday", 32
    SUNDAY = "sunday", "Sunday", 64


class Month(BaseEnum):

    JANUARY = "january", "January"
    FEBRUARY = "february", "February"
    MARCH = "march", "March"
    APRIL = "april", "April"
    MAY = "may", "May"
    JUNE = "june", "June"
    JULY = "july", "July"
    AUGUST = "august", "August"
    SEPTEMBER = "september", "September"
    OCTOBER = "october", "October"
    NOVEMBER = "november", "November"
    DECEMBER = "december", "December"


class TemplateType(BaseEnum):
    """
    Template type
    """

    STRING = "string", "String"
    HTML = "html", "HTML"


class TransactionStatus(BaseEnum):
    CREATED = "created", "Created"
    IN_PROCESS = "in_process", "In Processes"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"


class Country(BaseEnum):
    """
    Country code
    """

    INDIA = "IN", "India"


class AccessType(BaseEnum):
    PRIVATE = "private", "Private"
    PUBLIC = "public", "Public"
    PROTECTED = "protected", "Protected"


class MediaType(BaseEnum):
    IMAGE = "image", "Image"
    VIDEO = "video", "Video"
    AUDIO = "audio", "Audio"


class Status(BaseEnum):
    CREATED = "created", "Created"
    IN_PROCESS = "in_process", "In Process"
    LIVE = "live", "Live"
    OFFLINE = "offline", "Offline"
    DEACTIVATED = "deactivated", "Deactivated"


class BinaryStatus(BaseEnum):
    ACTIVE = "active", "Active"
    DEACTIVATED = "deactivated", "Deactivated"


class RelationshipStatus(BaseEnum):
    CREATED = "created", "Created"
    IN_REVIEW = "in_review", "In Review"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    ACTIVE = "active", "Active"
    DEACTIVATED = "deactivated", "Deactivated"


class RelationshipAction(BaseEnum):
    RAISE_REVIEW = "raise_review", "Raise Review"
    APPROVE = "approve", "Approve"
    REJECT = "reject", "Reject"
    ACTIVATE = "activate", "Activate"
    DEACTIVATE = "deactivate", "Deactivate"


class BookingStatus(BaseEnum):
    CREATED = "created", "Created"
    BOOKED = "booked", "Booked"
    RELEASED = "released", "Released"


class FileStorageLocation(BaseEnum):
    S3 = "s3", "Amazon S3"
    GOOGLE_CLOUD = "google_cloud", "Google Cloud"
    LOCAL = "local", "Local"


class MediaFileStatus(BaseEnum):
    CREATED = "created", "Created"
    IN_CLOUD = "in_cloud", "Stored in cloud"
    IN_CDN = "in_cdn", "Distributed by CDN"


class FileAccessLevel(BaseEnum):
    PUBLIC = "public", "Public"
    PROTECTED = "protected", "Protected"
    PRIVATE = "private", "Private"


class DistanceUnit(BaseEnum):
    METER = "m", "Meter"
    KILOMETER = "km", "Kilometer"
    MILES = "mi", "Miles"
    FEET = "ft", "Feet"


class PlaceType(BaseEnum):
    CITY = "city", "City"
    STATE = "state", "State"
    COUNTRY = "country", "Country"


class AddressType(BaseEnum):
    HOME = "home", "Home"
    OFFICE = "office", "Office"
    TEMP = "temp", "Temporary"


class UpdateType(BaseEnum):
    CREATED = "created", "Created"
    UPDATED = "updated", "Updated"
    DELETED = "deleted", "Deleted"
    ACTION = "action", "Action"


class TransactionType(BaseEnum):
    CREDIT = "credit", "Credit"
    DEBIT = "debit", "Debit"


class HTTPRequestType(BaseEnum):
    POST = "POST", "post"
    GET = "GET", "get"
    PATCH = "PATCH", "patch"
    PUT = "PUT", "put"
    OPTIONS = "OPTIONS", "options"
    DELETE = "DELETE", "delete"


class ValueType(BaseEnum):
    PERCENTAGE = "percentage"
    ABSOLUTE = "absolute"


class ResourceOperation(BaseEnum):
    CREATE = "create", "Create", 1
    READ = "read", "Read", 2
    UPDATE = "update", "Update", 4
    DELETE = "delete", "Delete", 8
