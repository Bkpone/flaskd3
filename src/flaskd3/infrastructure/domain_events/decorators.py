from functools import wraps

from flaskd3.appcore.core.application_core import app_core
from flaskd3.types.base_entity import BaseEntity


def send_domain_event(domain_name):
    """
    Send domain event
    :param domain_name:
    :return:
    """

    def send_domain_event_inner(func):
        """

        :param func:
        :return:
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper
            :param args:
            :param kwargs:
            :return:
            """

            def write_de(item, writer):
                if isinstance(item, (list, set, tuple)):
                    for i in item:
                        write_de(i, writer)
                else:
                    if isinstance(item, BaseEntity):
                        writer.write(item)
            response = func(*args, **kwargs)
            domain_event_service = app_core.get_infra_service("domain_event_service")
            domain_event_writer = domain_event_service.get_event_writer_for_api(domain_name)
            write_de(response, domain_event_writer)
            domain_event_writer.flush()
            return response

        return wrapper

    return send_domain_event_inner


def with_domain_event(func):
    """
    Handle DB commits
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Wrapper
        :param args:
        :param kwargs:
        :return:
        """
        domain_event_service = app_core.get_infra_service("domain_event_service")
        kwargs["domain_event_service"] = domain_event_service
        return func(*args, **kwargs)

    return wrapper
