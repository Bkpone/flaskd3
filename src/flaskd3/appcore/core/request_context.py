import os

from flask import g

from flaskd3.common.constants import ApplicationEnv, SUPER_ORG_ID


def set_current_user(user):
    g.current_user = user


def get_current_user():
    return g.get("current_user")


def get_organisation_id():
    return g.get("organisation_id")


def get_tenant_id():
    return g.get("tenant_id")


def set_organisation_id(organisation_id):
    g.organisation_id = organisation_id


def set_tenant_id(tenant_id):
    """Organisation Id is also the tenant Id"""
    if not tenant_id:
        tenant_id = SUPER_ORG_ID
    g.tenant_id = tenant_id


def get_currency():
    return g.get("functional_currency")


def set_currency(functional_currency):
    g.functional_currency = functional_currency


def get_active_env():
    return ApplicationEnv(os.getenv("APP_ENV", "local"))
