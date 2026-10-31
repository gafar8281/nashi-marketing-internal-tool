"""Checks that uploaded CSVs are the expected files before any processing runs."""
import pandas as pd

SALLA_REQUIRED_COLUMN = 'sku_number'
ERP_REQUIRED_COLUMN = 'sticker_number'

SWAPPED_MESSAGE = 'this looks like the other file. Please swap the two uploads.'


class InputFileError(Exception):
    """An uploaded file can't be used. The message is shown to the user."""


def _read_columns(file, **read_csv_kwargs):
    """Returns the stripped column names, leaving the file rewound for the real read."""
    file.seek(0)
    try:
        header = pd.read_csv(file, nrows=0, **read_csv_kwargs)
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
    return set(header.columns.str.strip())


def validate_salla_file(file):
    columns = _read_columns(file, header=1)
    if SALLA_REQUIRED_COLUMN in columns:
        return
    # The ERP file keeps its column names on row 1, one row above where Salla's are.
    if ERP_REQUIRED_COLUMN in _read_columns(file):
        raise InputFileError(SWAPPED_MESSAGE)
    raise InputFileError(
        'the "sku_number" column was not found on row 2. '
        'Please upload the Salla Product Quantities export.'
    )


def validate_erp_file(file):
    columns = _read_columns(file)
    if ERP_REQUIRED_COLUMN in columns:
        return
    # The Salla file keeps its column names on row 2, one row below where the ERP's are.
    if SALLA_REQUIRED_COLUMN in _read_columns(file, header=1):
        raise InputFileError(SWAPPED_MESSAGE)
    raise InputFileError(
        'the "sticker_number" column was not found on row 1. '
        'Please upload the ERP sticker export.'
    )
