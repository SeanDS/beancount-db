# Beancount Deutsche Bank importer
Beancount importer for Deutsche Bank account CSV exports.

## Usage
```python
from beancount_db import CurrentAccount

_BRANCH = "000"
_NUMBER = "0000000"
_ACCOUNT = "Assets:Deutsche-Bank:Current"
_CURRENCY = "EUR"
_ENCODING = "ISO-8859-15"

CONFIG = [
    CurrentAccount(
        _BRANCH,
        _NUMBER,
        _ACCOUNT,
        currency=_CURRENCY,
        file_encoding=_ENCODING,
    ),
]
```

## Development
To set up your development environment, please run the following from the `beancount-db`
repository root directory:

```bash
pip install -e .[dev]
```

After installation, run `pre-commit install`. This sets up some linting and code
formatting pre-commit checks.
