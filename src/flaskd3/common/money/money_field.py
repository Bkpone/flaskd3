from marshmallow import fields
from marshmallow.exceptions import ValidationError

from flaskd3.common.money.constants import CurrencyType
from flaskd3.common.money.exceptions import IncorrectMoneyInputError
from flaskd3.common.money.money import Money


class MoneyField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return ""
        if not isinstance(value, Money):
            raise ValidationError("value should be of type Money found type: {}".format(value.__class__.__name__))
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        if not value and value != 0:
            raise ValidationError("Empty value not deserializable to Money")
        if isinstance(value, Money):
            return value
        try:
            if isinstance(value, dict):
                amount = value.get("amount")
                if amount is None:
                    raise ValidationError("Invalid Money object of type dict: {}".format(value))
                currency = value.get("currency")
                if not currency:
                    currency = value.get("currencyType")
                if not currency:
                    currency = value.get("currency_type")
                if currency:
                    currency = CurrencyType(currency)
                else:
                    raise IncorrectMoneyInputError(
                        "Currency is required when deserializing object of type Money.",
                    )
                money = Money(str(amount), currency=currency)
            else:
                money = Money(value)
        except IncorrectMoneyInputError as e:
            raise ValidationError("Failed creating money object with error: {}".format(e))
        return money
