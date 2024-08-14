from decimal import ROUND_HALF_EVEN, Decimal

from flask import current_app

from flaskd3.appcore.core.request_context import get_currency
from flaskd3.common.exceptions import InvalidStateException
from flaskd3.common.money.constants import PRECISION, CurrencyType
from flaskd3.common.money.exceptions import (
    CurrencyMismatchError,
    IncorrectMoneyInputError,
    InvalidOperationException,
)


class Money(object):
    """
    stores amount without losing any precision ,round of it to two decimal places
    whenever asked explicitly

    """

    def __init__(self, amount=None, currency=None):
        if not amount:
            amount = Decimal(0)
        if not currency:
            currency = get_currency()
            if currency == None:
                currency = current_app.config["DEFAULT_CURRENCY"]
            if currency == None:
                raise InvalidStateException(
                    "Could not resolve currency at various levels."
                )
        if currency:
            if not isinstance(currency, CurrencyType):
                currency = CurrencyType(currency)
        self._currency = currency
        if isinstance(amount, Money):
            self._amount = amount._amount
            self._currency = amount._currency
        elif isinstance(amount, dict):
            self._amount = Decimal(amount["amount"])
            self._currency = CurrencyType(amount["currency"])
        elif isinstance(amount, float):
            raise IncorrectMoneyInputError(
                "Initialization using float not supported",
            )
        elif isinstance(amount, str):
            values = amount.split(" ")
            if len(values) > 2:
                raise IncorrectMoneyInputError(
                    "Cannot initialize with amount %s" % amount,
                )
            try:
                self._amount = Decimal(values[0])
                self._currency = (
                    CurrencyType(
                        values[1],
                    )
                    if len(values) == 2
                    else currency
                )
            except Exception as e:
                raise IncorrectMoneyInputError(
                    "Unable to create money for amount: {} "
                    "due to reason: {}".format(amount, e)
                )
        elif isinstance(amount, Decimal):
            self._amount = amount
        else:
            try:
                self._amount = Decimal(str(amount))
            except Exception as e:
                raise IncorrectMoneyInputError(
                    "Unable to create money for amount: {} "
                    "due to reason: {}".format(amount, e)
                )

    def data(self):
        return dict(amount=str(self.amount), currency=self._currency.value)

    def dict(self):
        return dict(amount=self.amount, currency=self._currency)

    def to_dict(self):
        return dict(amount=str(self.amount), currency=self._currency)

    @property
    def amount(self):
        return self._amount.quantize(Decimal(".01"), rounding=ROUND_HALF_EVEN)

    @property
    def currency(self):
        return self._currency

    def __str__(self):
        return "{} {}".format(self.amount, self._currency.value)

    def __repr__(self):
        return str(self)

    def __float__(self):
        return float(self.amount)

    def __int__(self):
        return int(self.amount)

    def __pos__(self):
        return Money(amount=self._amount, currency=self._currency)

    def __neg__(self):
        return Money(amount=-self._amount, currency=self._currency)

    def __add__(self, other):
        if isinstance(other, Money):
            if self._currency == other._currency:
                return Money(
                    amount=self._amount + other._amount, currency=self._currency
                )
            else:
                raise CurrencyMismatchError("Adding two different currencies")
        else:
            return Money(
                amount=self._amount + Decimal(str(other)), currency=self._currency
            )

    def __sub__(self, other):
        if isinstance(other, Money):
            if self._currency == other._currency:
                return Money(
                    amount=self._amount - other._amount, currency=self._currency
                )
            else:
                raise CurrencyMismatchError(
                    "Subtracting two different currencies",
                )

        else:
            return Money(
                amount=self._amount - Decimal(str(other)), currency=self._currency
            )

    def __rsub__(self, other):
        # In the case where both values are Money, the left hand one will be
        # called. In the case where we are subtracting Money from another
        # value, we want to disallow it
        raise TypeError("Cannot subtract Money from %r" % other)

    def __mul__(self, other):
        if isinstance(other, Money):
            raise InvalidOperationException(
                "Cannot multiply monetary quantities",
            )
        return Money(amount=self._amount * Decimal(str(other)), currency=self._currency)

    def __abs__(self):
        return Money(abs(self._amount), self._currency)

    def __truediv__(self, other):
        """
        We allow division by non-money numeric values but dividing by
        another Money value is undefined
        """
        if isinstance(other, Money):
            raise InvalidOperationException(
                "Cannot divide two monetary quantities",
            )
        return Money(amount=self._amount / Decimal(str(other)), currency=self._currency)

    __div__ = __truediv__

    def __floordiv__(self, other):
        raise InvalidOperationException(
            "Floor division not supported for monetary quantities",
        )

    def __rtruediv__(self, other):
        raise InvalidOperationException("Cannot divide by monetary quantities")

    __rdiv__ = __rtruediv__

    # Commutative operations
    __radd__ = __add__
    __rmul__ = __mul__

    # Boolean
    def __bool__(self):
        return self._amount != 0

    __nonzero__ = __bool__

    # Comparison operators
    def __eq__(self, other):
        if isinstance(other, Money):
            return self.amount == other.amount and self._currency == other._currency
        # Allow comparison to 0
        if (other == 0) and (self.amount == 0):
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if isinstance(other, Money):
            if self._currency != other._currency:
                raise CurrencyMismatchError("Comparing different currencies")
            return self.amount < other.amount
        else:
            return self.amount < Decimal(str(other))

    def __gt__(self, other):
        if isinstance(other, Money):
            if self._currency != other._currency:
                raise CurrencyMismatchError("Comparing different currencies")
            return self.amount > other.amount
        else:
            return self.amount > Decimal(str(other))

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def split_into_almost_equal_parts(self, n):
        """
        split value into n almost equal parts
        :param value: value to split
        :param n: split into this no of parts
        :return:
        """
        value = self._amount
        split_value = round(value / n, PRECISION)
        split_values = [Money(split_value, self._currency)] * (n - 1)
        last_value = self - sum(split_values)
        split_values.append(last_value)
        return split_values

    def sum(self, other):
        if isinstance(other, Money):
            if self._currency == other._currency:
                self._amount += other._amount
                return self
            else:
                raise CurrencyMismatchError("Adding two different currencies")
        else:
            self._amount += Decimal(str(other))
            return self

    @property
    def subunit(self):
        return int(self._amount * 100)

    @property
    def raw_decimal(self):
        return self._amount

    @classmethod
    def from_subunits(cls, amount_in_subunits, currency):
        return cls(amount=amount_in_subunits/100, currency=currency)
