"""Streamlit interface for updating stock in the Salla file. Run: streamlit run app.py

Uploads stay in this session's memory and are never written to disk. Don't add
st.cache_data around them: that cache is shared by all sessions.
"""
from dataclasses import dataclass

import pandas as pd
import streamlit as st

from main import (
    get_cleaned_erp_data,
    read_salla_file,
    salla_csv_bytes,
    update_available_quantity,
)
from validation import InputFileError, validate_erp_file, validate_salla_file

TITLE = 'Salla Stock Updater'
PROCESS_LABEL = 'Process Files'


@dataclass
class Result:
    total_count: int
    checked_count: int
    in_stock_count: int
    out_of_stock_count: int
    updated: pd.DataFrame
    csv_bytes: bytes
    file_name: str


def process(salla_file, erp_file):
    """Runs the shared stock logic on the uploads. Returns None if a file was rejected."""
    for file, validate in ((salla_file, validate_salla_file), (erp_file, validate_erp_file)):
        try:
            validate(file)
        except InputFileError as error:
            show_file_problem(file, str(error))
            return None

    salla_df = read_salla_file(salla_file)
    _, erp_sticker_numbers = get_cleaned_erp_data(erp_file)

    # Without stickers every product would be set out of stock, which looks like a real result.
    if not erp_sticker_numbers:
        show_file_problem(erp_file, 'no valid sticker numbers were found in this file.')
        return None

    updated, in_stock_count, out_of_stock_count = update_available_quantity(salla_df, erp_sticker_numbers)
    return Result(
        total_count=len(salla_df),
        checked_count=in_stock_count + out_of_stock_count,
        in_stock_count=in_stock_count,
        out_of_stock_count=out_of_stock_count,
        updated=updated,
        csv_bytes=salla_csv_bytes(updated),
        file_name=salla_file.name,
    )


def show_file_problem(file, message):
    st.error(f'Problem with {file.name}: {message}')


def show_result(result):
    st.success(f'Done. Updated available_quantity for {result.checked_count:,} products.')

    columns = st.columns(4)
    columns[0].metric('Salla products', f'{result.total_count:,}')
    columns[1].metric('In stock', f'{result.in_stock_count:,}')
    columns[2].metric('Out of stock', f'{result.out_of_stock_count:,}')
    columns[3].metric('Not checked', f'{result.total_count - result.checked_count:,}')

    if result.checked_count and not result.in_stock_count:
        st.warning(
            'None of the Salla products were found in the ERP file, so every checked '
            'product is set to 0. Please check that these are the right files.'
        )

    st.download_button(
        'Download updated Salla file (CSV)',
        data=result.csv_bytes,
        file_name=result.file_name,
        mime='text/csv',
        type='primary',
    )

    st.subheader('Preview')
    st.dataframe(result.updated, hide_index=True)


st.set_page_config(page_title=TITLE, page_icon='📦')

st.title(TITLE)
st.write('Update available_quantity in the Salla file: 1 if the product has a sticker in the ERP, 0 if not.')
st.markdown(
    '1. Upload the **Salla Product Quantities** CSV in the first box.\n'
    '2. Upload the **ERP sticker** CSV in the second box.\n'
    f'3. Click **{PROCESS_LABEL}**, check the preview, then download the updated Salla file.'
)
st.caption(
    'Products marked Not checked keep their existing value. '
    'Your files are used only to produce this result and are not saved.'
)

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
