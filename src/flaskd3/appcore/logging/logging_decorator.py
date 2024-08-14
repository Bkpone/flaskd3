# coding=utf-8
"""
Logging Decorator
"""
from __future__ import absolute_import

import functools
import logging
import traceback

LOG = logging.getLogger(__name__)


# Should not be used on @staticmethod or @classmethod. This will fail.
def log_args(logger=None, only_on_exception=False):
    """
    log args
    :param logger:
    :param only_on_exception:
    :return:
    """

    def decorator(func):
        """
        log args decorator
        :param func:
        :return:
        """
        try:
            argnames = func.func_code.co_varnames[: func.func_code.co_argcount]
        except Exception:
            argnames = None
        try:
            fname = func.func_name
        except Exception:
            fname = None

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper
            :param args:
            :param kwargs:
            :return:
            """
            argument_list = []
            if argnames:
                for entry in zip(argnames, args):
                    name = entry[0]
                    value = entry[1]
                    argument_list.append("{0}={1}".format(name, value))
            else:
                for arg in args:
                    argument_list.append("{0}".format(arg))

            for entry in kwargs.items():
                argument_list.append("{0}={1}".format(entry[0], entry[1]))

            argument_values = ", ".join(argument_list)
            log = logger if logger else LOG
            if not only_on_exception:
                log.info("Function:[%s] called with args: %s", fname, argument_values)
            try:
                return func(*args, **kwargs)
            except:
                if only_on_exception:
                    log.error(traceback.format_exc())
                    log.exception("Function:[%s] called with args: %s", fname, argument_values)
                raise

        return wrapper

    return decorator
