"""Checks that uploaded CSVs are the expected files before any processing runs."""
import pandas as pd

from main import AVAILABLE_QUANTITY_COLUMN

SALLA_SKU_COLUMN = 'sku_number'
SALLA_REQUIRED_COLUMNS = (SALLA_SKU_COLUMN, AVAILABLE_QUANTITY_COLUMN)
ERP_REQUIRED_COLUMN = 'sticker_number'

SWAPPED_MESSAGE = 'this looks like the other file. Please swap the two uploads.'


class InputFileError(Exception):
    """An uploaded file can't be used. The message is shown to the user."""


def _read_columns(file):
    """Returns the column names from row 1, leaving the file rewound for the real read."""
    file.seek(0)
    try:
        header = pd.read_csv(file, nrows=0)
    except pd.errors.EmptyDataError:
        raise InputFileError('the file is empty.') from None
    except pd.errors.ParserError:
        raise InputFileError('the file could not be read as a CSV.') from None
    except UnicodeDecodeError:
        raise InputFileError(
            'the file has an unsupported text encoding. '
            'In Excel, use Save As and choose "CSV UTF-8".'
        ) from None
    finally:
        file.seek(0)
    return list(header.columns)


def _stripped(columns):
    return {column.strip() for column in columns}


def validate_salla_file(file):
    columns = _read_columns(file)
    # Matched exactly: the Salla header is returned untouched, so it can't be tidied up to fit.
    missing = [column for column in SALLA_REQUIRED_COLUMNS if column not in columns]
    if not missing:
        return
    if ERP_REQUIRED_COLUMN in _stripped(columns):
        raise InputFileError(SWAPPED_MESSAGE)
    names = ' and '.join(f'"{column}"' for column in missing)
    found = 'column was' if len(missing) == 1 else 'columns were'
    raise InputFileError(
        f'the {names} {found} not found on row 1. '
        'Please upload the Salla Product Quantities export.'
    )


def validate_erp_file(file):
    columns = _stripped(_read_columns(file))
    if ERP_REQUIRED_COLUMN in columns:
        return
    if SALLA_SKU_COLUMN in columns:
        raise InputFileError(SWAPPED_MESSAGE)
    raise InputFileError(
        'the "sticker_number" column was not found on row 1. '
        'Please upload the ERP sticker export.'
    )
