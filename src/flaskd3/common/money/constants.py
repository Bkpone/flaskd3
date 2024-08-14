from flaskd3.types.base_enum import BaseEnum


class CurrencyType(BaseEnum):
    INR = "INR", "Indian Rupee"
    AED = "AED", "Emirati Dirham"
    WLT = "WLT", "Wallet balance"


PRECISION = 2
