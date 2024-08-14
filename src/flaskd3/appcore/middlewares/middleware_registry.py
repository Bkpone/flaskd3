from flaskd3.appcore.middlewares.common_middlewares import (
    before_request,
    after_request,
)
from flaskd3.appcore.middlewares.exception_middleware import exception_handler


def register_middleware(app):
    """
    register the error handlers
    :param app:
    :return:
    """
    app.before_request_funcs = {None: [before_request]}
    app.after_request_funcs = {None: [after_request]}
    app.register_error_handler(Exception, exception_handler)
