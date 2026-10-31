"""Checks that uploaded CSVs are the expected files before any processing runs.

Errors carry a code rather than display text so the UI can show them in the
selected language (see the "error_*" keys in i18n.py).
"""
import pandas as pd

SALLA_REQUIRED_COLUMN = 'sku_number'
ERP_REQUIRED_COLUMN = 'sticker_number'


class InputFileError(Exception):
    """An uploaded file can't be used. `code` selects the message shown to the user."""

    def __init__(self, code):
        super().__init__(code)
        self.code = code


def _read_columns(file, **read_csv_kwargs):
    """Returns the stripped column names, leaving the file rewound for the real read."""
    file.seek(0)
    try:
        header = pd.read_csv(file, nrows=0, **read_csv_kwargs)
    except pd.errors.EmptyDataError:
        raise InputFileError('empty') from None
    except pd.errors.ParserError:
        raise InputFileError('unreadable') from None
    except UnicodeDecodeError:
        raise InputFileError('encoding') from None
    finally:
        file.seek(0)
    return set(header.columns.str.strip())


def validate_salla_file(file):
    columns = _read_columns(file, header=1)
    if SALLA_REQUIRED_COLUMN in columns:
        return
    # The ERP file keeps its column names on row 1, one row above where Salla's are.
    if ERP_REQUIRED_COLUMN in _read_columns(file):
        raise InputFileError('swapped')
    raise InputFileError('missing_column_salla')


def validate_erp_file(file):
    columns = _read_columns(file)
    if ERP_REQUIRED_COLUMN in columns:
        return
    # The Salla file keeps its column names on row 2, one row below where the ERP's are.
    if SALLA_REQUIRED_COLUMN in _read_columns(file, header=1):
        raise InputFileError('swapped')
    raise InputFileError('missing_column_erp')
