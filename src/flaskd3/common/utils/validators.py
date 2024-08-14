import re

from marshmallow.exceptions import ValidationError

from flaskd3.common.utils import dateutils

COUPON_REGEX = re.compile(r"^[A-Z0-9]{1}[A-Z0-9-_]+[A-Z0-9]{1}$")


def validate_empty_string(value):
    if value == "":
        raise ValidationError("Field value cannot be blank")

    if value.isspace():
        raise ValidationError("Field value cannot consist of just whitespace")


def validate_phone_number(value):
    if not re.compile(r"[-+0-9]+").match(value):
        raise ValidationError("Please enter a valid phone number")


def validate_numeric_string(value):
    if not value.isdigit():
        raise ValidationError("Field value should be numeric")


def validate_date(value):
    if dateutils.is_naive(value):
        raise ValidationError("Timezone information missing")


def validate_coupons(coupons):
    if isinstance(coupons, str):
        coupons = [coupons]
    invalid_coupons = list()
    for coupon in coupons:
        if COUPON_REGEX.match(coupon) is None:
            invalid_coupons.append(coupon)
    if invalid_coupons:
        raise ValidationError(
            f"Invalid coupons : {invalid_coupons}. Can only contain A-Z, 0-9, -, _ , have a minimum of 3 characters and can only start and end with a letter."
        )
