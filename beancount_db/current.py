"""Beancount importer for Deutsche Bank current account CSV exports."""

import csv
import re
from datetime import datetime

from beancount.core import data
from beancount.core.amount import Amount
from beancount.ingest.importer import ImporterProtocol
from . import format_number


class InvalidFormatError(ValueError):
    """Invalid file format."""

    def __init__(self, message, lineno=None, **kwargs):
        if lineno is not None:
            message += f" (line {lineno})"
        super().__init__(message, **kwargs)


class CurrentAccount(ImporterProtocol):
    DATA_HEADERS = (
        "Booking date",
        "Value date",
        "Transaction Type",
        "Beneficiary / Originator",
        "Payment Details",
        "IBAN",
        "BIC",
        "Customer Reference",
        "Mandate Reference",
        "Creditor ID",
        "Compensation amount",
        "Original Amount",
        "Ultimate creditor",
        "Number of transactions",
        "Number of cheques",
        "Debit",
        "Credit",
        "Currency",
    )

    DATE_FORMAT = "%m/%d/%Y"

    def __init__(self, branch, number, account, currency="EUR", file_encoding="utf-8"):
        self.account = account
        self.currency = currency
        self.file_encoding = file_encoding

        self._expected_header_regex = re.compile(
            r"^Transactions\s.*;;;Customer\snumber:\s"
            + re.escape(branch)
            + r"\s"
            + re.escape(number)
            + r"$",
            flags=re.MULTILINE,
        )
        self._from_to_regex = re.compile(
            r"^(\d\d\/\d\d\/\d\d\d\d) - (\d\d\/\d\d\/\d\d\d\d)$"
        )
        self._starting_balance_regex = re.compile(
            r"^Old\sbalance:;;;;((\d+)(,(\d+))*.\d\d);" + re.escape(currency) + r"$"
        )

        self._date_from = None
        self._date_to = None
        self._starting_balance = None
        self._finishing_balance = None

    def name(self):
        """Include the filing account in the name."""
        return f"{self.__class__.__module__} {self.__class__.__name__}"

    def identify(self, file_):
        """Identify whether the passed file can be handled by this importer."""
        return self._expected_header_regex.match(file_.contents())

    def file_account(self, _):
        """The account against which we post transactions."""
        return self.account

    def file_date(self, file_):
        """The optional renamed account filename."""
        self.extract(file_)

        return self._date_to

    def extract(self, file_, existing_entries=None):
        entries = []
        lineno = 0

        with open(file_.name, encoding=self.file_encoding) as fobj:

            def next_line():
                nonlocal lineno
                lineno += 1
                return fobj.readline().strip()

            # Header with account name and number.
            line = next_line()

            if not self._expected_header_regex.match(line):
                raise InvalidFormatError(f"Unexpected header '{line}'", lineno)

            # From and to dates.
            line = next_line()
            from_and_to = self._from_to_regex.match(line)
            if not from_and_to or len(from_and_to.groups()) != 2:
                raise InvalidFormatError(f"Unexpected from and to dates '{line}'")
            self._date_from = datetime.strptime(
                from_and_to.group(1), self.DATE_FORMAT
            ).date()
            self._date_to = datetime.strptime(
                from_and_to.group(2), self.DATE_FORMAT
            ).date()

            # Starting balance.
            line = next_line()
            starting_balance = self._starting_balance_regex.match(line)
            if not starting_balance or len(starting_balance.groups()) != 4:
                raise InvalidFormatError(f"Unexpected old balance '{line}'")
            self._starting_balance = starting_balance.group(0)

            # "Transactions pending are not included in this report."
            line = next_line()
            line4text = "Transactions pending are not included in this report."
            if line != line4text:
                raise InvalidFormatError(
                    f"Unexpected line '{line}' (expected {line4text})"
                )

            # Data entries.
            reader = csv.DictReader(
                fobj, delimiter=";", quoting=csv.QUOTE_MINIMAL, quotechar='"'
            )

            # Check headers.
            lineno += 1
            if set(reader.fieldnames) != set(self.DATA_HEADERS):
                expected = ";".join(self.DATA_HEADERS)
                raise InvalidFormatError(
                    f"Unexpected data headers (expected {expected})", lineno
                )

            for line in reader:
                lineno += 1

                if line["Booking date"] == "Account balance":
                    # Last line. Balance value is in the "Payment Details" column,
                    # currency in the "IBAN" column.
                    if line["IBAN"] != self.currency:
                        raise InvalidFormatError(
                            f"Unexpected currency {line['Currency']}", lineno
                        )

                    self._finishing_balance = format_number(line["Payment Details"])
                else:
                    if line["Currency"] != self.currency:
                        raise InvalidFormatError(
                            f"Unexpected currency {line['Currency']}", lineno
                        )

                    if line["Debit"]:
                        if line["Credit"]:
                            raise InvalidFormatError(
                                "Cannot have both debit and credit values", lineno
                            )
                        value = format_number(line["Debit"])
                    elif line["Credit"]:
                        value = format_number(line["Credit"])
                    else:
                        raise InvalidFormatError(
                            "Neither debit not credit value found", lineno
                        )

                    meta = data.new_metadata(file_.name, lineno)
                    date = datetime.strptime(
                        line["Value date"], self.DATE_FORMAT
                    ).date()
                    amount = Amount(value, self.currency)
                    payee = line["Beneficiary / Originator"].strip()
                    narration = ""

                    postings = [
                        data.Posting(self.account, amount, None, None, None, None)
                    ]

                    entries.append(
                        data.Transaction(
                            meta=meta,
                            date=date,
                            flag=self.FLAG,
                            payee=payee,
                            narration=narration,
                            tags=data.EMPTY_SET,
                            links=data.EMPTY_SET,
                            postings=postings,
                        )
                    )

        return entries
