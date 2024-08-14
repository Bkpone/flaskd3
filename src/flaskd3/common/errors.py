from flaskd3.common.exceptions import FDError


class CommonError(FDError):

    ENTITY_TO_DB_CONVERSION_MAP_MISSING = "0001", "Db conversion map missing"
    ENTITY_TO_DB_CONVERSION_ERROR = "0002", "Db conversion Error"
    DUPLICATE_REPO_FOUND = "0003", "Duplicate Repo found. Please contact escalations."


class ErrorDomains:
    USER_ERROR_DOMAIN = "01"
    OTP_ERROR_DOMAIN = "02"
