import datetime
from _pydecimal import Decimal as pyDecimal
from decimal import Decimal
from enum import Enum

from flaskd3.types.base_dto import BaseDto
from flaskd3.types.base_entity import BaseEntity
from flaskd3.types.iter_base import IterBase
from flaskd3.types.map_object import MapObject
from flaskd3.types.mutable_value_object import MutableValueObject
from flaskd3.types.value_object import ValueObject
from flaskd3.common.money import Money
from flaskd3.common.utils import dateutils


def make_jsonify_ready(obj):
    if isinstance(obj, (list, set)):
        response_list = list()
        for item in obj:
            response_list.append(make_jsonify_ready(item))
        return response_list
    if isinstance(obj, dict):
        if not obj:
            return None
        response_dict = dict()
        for key, val in obj.items():
            response_dict[key] = make_jsonify_ready(val)
        return response_dict
    if isinstance(obj, pyDecimal):
        return float(obj)
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, (ValueObject, MutableValueObject)):
        return make_jsonify_ready(obj.data())
    if isinstance(obj, BaseEntity):
        return make_jsonify_ready(obj.data())
    if isinstance(obj, IterBase):
        return make_jsonify_ready(obj.list())
    if isinstance(obj, (datetime.datetime, datetime.time)):
        return dateutils.to_string(obj)
    if isinstance(obj, datetime.date):
        return dateutils.date_to_string(obj)
    if isinstance(obj, Money):
        return make_jsonify_ready(obj.data())
    if isinstance(obj, BaseDto):
        return make_jsonify_ready(obj.data())
    if isinstance(obj, MapObject):
        return make_jsonify_ready(obj.data())
    return obj
