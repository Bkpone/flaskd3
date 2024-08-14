# coding=utf-8
"""
extensions
"""
import logging

from flask_mail import Mail
from flask_marshmallow import Marshmallow

logger = logging.getLogger(__name__)

ma = Marshmallow()
external_servers = dict()


def register_extensions(app):
    """
    Registering extensions
    :param app:
    :return:
    """
    ma.init_app(app)
    external_servers["mail"] = Mail(app)
