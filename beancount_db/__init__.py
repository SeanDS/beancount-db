"""Beancount importer for Deutsche Bank account CSV exports."""

from beancount.core.number import Decimal
from .current import CurrentAccount


def format_number(value):
    return Decimal(value.replace(",", ""))


ALL = (CurrentAccount, format_number)
