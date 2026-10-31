"""Streamlit interface for the Salla out-of-stock check. Run: streamlit run app.py

Uploads stay in this session's memory and are never written to disk. Don't add
st.cache_data around them: that cache is shared by all sessions.
"""
from dataclasses import dataclass
from datetime import date

import pandas as pd
import streamlit as st

from main import find_out_of_stock_items, get_cleaned_erp_data, get_cleaned_salla_data
from validation import InputFileError, validate_erp_file, validate_salla_file

SALLA_HEADER_ROW = 1

TITLE = 'Salla Out-of-Stock Checker'
PROCESS_LABEL = 'Process Files'


@dataclass
class Result:
    total_count: int
    checked_count: int
    matched_any: bool
    out_of_stock: pd.DataFrame
    skipped: pd.DataFrame
    csv_bytes: bytes


def process(salla_file, erp_file):
    """Runs the existing script logic on the uploads. Returns None if a file was rejected."""
    for file, validate in ((salla_file, validate_salla_file), (erp_file, validate_erp_file)):
        try:
            validate(file)
        except InputFileError as error:
            show_file_problem(file, str(error))
            return None

    salla_raw = pd.read_csv(salla_file, header=SALLA_HEADER_ROW)
    salla_file.seek(0)
    salla_cleaned = get_cleaned_salla_data(salla_file)
    _, erp_sticker_numbers = get_cleaned_erp_data(erp_file)

    # Without stickers every product would be reported out of stock, which looks like a real result.
    if not erp_sticker_numbers:
        show_file_problem(erp_file, 'no valid sticker numbers were found in this file.')
        return None

    out_of_stock = find_out_of_stock_items(salla_cleaned, erp_sticker_numbers)
    return Result(
        total_count=len(salla_raw),
        checked_count=len(salla_cleaned),
        matched_any=len(out_of_stock) < len(salla_cleaned),
        out_of_stock=out_of_stock,
        # The cleaner keeps the original row index, so anything missing from it was skipped.
        skipped=salla_raw.loc[salla_raw.index.difference(salla_cleaned.index)],
        # The BOM makes Excel display the Arabic product data correctly.
        csv_bytes=out_of_stock.to_csv(index=False).encode('utf-8-sig'),
    )


def show_file_problem(file, message):
    st.error(f'Problem with {file.name}: {message}')


def show_result(result):
    st.success(f'Done. Found {len(result.out_of_stock):,} out-of-stock products.')

    columns = st.columns(4)
    columns[0].metric('Salla products', f'{result.total_count:,}')
    columns[1].metric('Checked', f'{result.checked_count:,}')
    columns[2].metric('Out of stock', f'{len(result.out_of_stock):,}')
    columns[3].metric('Skipped', f'{len(result.skipped):,}')

    if not result.matched_any:
        st.warning(
            'None of the Salla products were found in the ERP file, so every checked '
            'product is listed as out of stock. Please check that these are the right files.'
        )

    st.download_button(
        'Download result (CSV)',
        data=result.csv_bytes,
        file_name=f'salla_out_of_stock_{date.today():%Y-%m-%d}.csv',
        mime='text/csv',
        type='primary',
    )

    st.subheader('Preview')
    st.dataframe(result.out_of_stock, hide_index=True)

    if len(result.skipped):
        st.warning(
            f'{len(result.skipped):,} products could not be checked because no number could '
            'be read from the end of their SKU. They are not in the downloaded file.'
        )
        with st.expander('Show skipped products'):
            st.dataframe(result.skipped, hide_index=True)


st.set_page_config(page_title=TITLE, page_icon='📦')

st.title(TITLE)
st.write('Find the products listed on Salla that no longer have a sticker in the ERP.')
st.markdown(
    '1. Upload the **Salla Product Quantities** CSV in the first box.\n'
    '2. Upload the **ERP sticker** CSV in the second box.\n'
    f'3. Click **{PROCESS_LABEL}**, check the preview, then download the result.'
)
st.caption('Your files are used only to produce this result and are not saved.')

upload_columns = st.columns(2)
salla_file = upload_columns[0].file_uploader(
    'File 1: Salla Product Quantities (CSV)', type='csv', key='salla_upload'
)
erp_file = upload_columns[1].file_uploader(
    'File 2: ERP stickers (CSV)', type='csv', key='erp_upload'
)
if salla_file:
    upload_columns[0].caption(f'Selected: {salla_file.name}')
if erp_file:
    upload_columns[1].caption(f'Selected: {erp_file.name}')

# A result from earlier uploads must not stay on screen next to different files.
upload_ids = (salla_file and salla_file.file_id, erp_file and erp_file.file_id)
if st.session_state.get('upload_ids') != upload_ids:
    st.session_state.upload_ids = upload_ids
    st.session_state.result = None

if st.button(PROCESS_LABEL, disabled=not (salla_file and erp_file)):
    st.session_state.result = None
    with st.spinner('Processing your files...'):
        try:
            st.session_state.result = process(salla_file, erp_file)
        except Exception as error:
            st.error('Something went wrong while processing the files. Please check them and try again.')
            with st.expander('Technical details'):
                st.code(f'{type(error).__name__}: {error}')

# Kept in session_state because clicking download reruns this script.
if st.session_state.result is not None:
    show_result(st.session_state.result)
