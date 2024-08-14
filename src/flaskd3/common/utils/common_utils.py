# coding=utf-8
"""
common utils
"""
import datetime
import importlib
import inspect
import json
import logging
import os
import pkgutil
import re
import string
from hashlib import md5

from flaskd3.common.exceptions import InvalidStateException
from flaskd3.common.money.money import Money
from flaskd3.common.utils import dateutils

logger = logging.getLogger(__name__)


baseDigits = string.digits + string.ascii_letters


class DateTimeEncoder(json.JSONEncoder):
    """
    Date Time Encoder
    """

    def default(self, o):
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


def decode_bytes(message):
    """
    Decode
    :param message:
    :return:
    """
    return message.decode("utf-8")


def merge_dict(a, b, path=None):
    """
    >>> a = {"rt01": {"x": 1}, "rt02": {"x":2, "y": 4}}
    >>> b = {"rt01": {"y": 4, "x": 2}, "rt02": {"y": 2}}
    >>> merge(a, b)
    {'rt01': {'x': 2, 'y': 4}, 'rt02': {'x': 2, 'y': 2}}

    :param a:
    :param b:
    :param path:
    :return:
    """
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_dict(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass
            else:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a


def get_sub_modules(module, suffix=None):
    sub_modules = []
    pkg_dir = os.path.dirname(module.__file__)
    sub_module_names = [name for _, name, val1 in pkgutil.iter_modules([pkg_dir])]
    for sub_module_name in sub_module_names:
        sub_module_name = sub_module_name + suffix if suffix else sub_module_name
        try:
            sub_modules.append(importlib.import_module("." + sub_module_name, module.__name__))
        except ModuleNotFoundError:
            pass
    return sub_modules


def is_valid_email(email):
    regex = "^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
    return True if re.search(regex, email) else False


def get_domain_from_email(email):
    email_split = email.split("@")
    if len(email_split) < 2:
        raise RuntimeError("Invalid email ID")
    return email_split[-1]


def money_converter(value):
    return value if isinstance(value, Money) or value is None else Money(value)


def to_camel_case(value):
    first, *rest = value.split("_")
    return first + "".join([e.capitalize() for e in rest])


def to_snake_case(value):
    return "".join(["_" + i.lower() if i.isupper() else i for i in value]).lstrip("_")


def convert_key_to_camel_case(obj):
    return convert_key_style(obj, to_camel_case)


def convert_key_to_snake_case(obj):
    return convert_key_style(obj, to_snake_case)


def convert_key_style(obj, fun):
    if isinstance(obj, dict):
        return_dict = dict()
        for key, value in obj.items():
            return_dict[fun(key)] = convert_key_style(value, fun)
        return return_dict
    elif isinstance(obj, (list, set)):
        return [convert_key_style(e, fun) for e in obj]
    else:
        return obj


def search_class(
    modules,
    sub_module_name,
    class_filters,
    exclude_list,
    get_object,
    obj_parameters=None,
):
    store = dict()
    if sub_module_name:
        sub_module_name = "." + sub_module_name
    if not exclude_list:
        exclude_list = []
    if class_filters:
        for class_filter in class_filters:
            exclude_list.append(class_filter.__name__)
    for module in modules:
        packages = get_sub_modules(module, sub_module_name) if sub_module_name else [module]
        for package in packages:
            sub_module = get_sub_modules(package)
            for repository_module in sub_module:
                for name, obj in inspect.getmembers(repository_module):
                    if name in exclude_list:
                        continue
                    if inspect.isclass(obj) and (issubclass(obj, tuple(class_filters))):
                        get_name = getattr(obj, "get_name", None)
                        name = get_name() if get_name and callable(get_name) else getattr(obj, "name", obj.__name__)
                        if store.get(name):
                            raise InvalidStateException(
                                message="Duplicate {} found".format([cls.__name__ for cls in class_filters]),
                                description="found duplicate {}".format(name),
                            )
                        if get_object:
                            if obj_parameters:
                                store[name] = obj(**obj_parameters)
                            else:
                                store[name] = obj()
                        else:
                            store[name] = obj
    return store


def base_n_converter(value, base):
    if not value:
        return value
    digits = []
    while value:
        digits.append(baseDigits[int(value % base)])
        value = int(value / base)
    digits.reverse()
    return "".join(digits)


def convert_to_type(obj, class_obj):
    if isinstance(obj, str):
        if issubclass(class_obj, datetime.date):
            return dateutils.date_from_string(obj)
        elif issubclass(class_obj, datetime.datetime):
            return dateutils.from_string(obj)
    else:
        return class_obj(**obj)
    return None


def urljoin(*args):
    return "/".join(map(lambda x: str(x).strip("/"), args))


def generate_unique_hash_for_dict(request_dict):
    return str(md5(json.dumps(request_dict).encode()).hexdigest())
