"""Streamlit interface for the Salla out-of-stock check. Run: streamlit run app.py

Uploads stay in this session's memory and are never written to disk. Don't add
st.cache_data around them: that cache is shared by all sessions.
"""
from dataclasses import dataclass
from datetime import date

import pandas as pd
import streamlit as st

from i18n import LANGUAGES, t
from main import find_out_of_stock_items, get_cleaned_erp_data, get_cleaned_salla_data
from validation import InputFileError, validate_erp_file, validate_salla_file

SALLA_HEADER_ROW = 1

RTL_CSS = """
<style>
.stApp { direction: rtl; }
[data-testid="stMarkdownContainer"], [data-testid="stMetric"], .stAlert { text-align: right; }
[data-testid="stDataFrame"] { direction: ltr; }
</style>
"""


@dataclass
class Result:
    total_count: int
    checked_count: int
    matched_any: bool
    out_of_stock: pd.DataFrame
    skipped: pd.DataFrame
    csv_bytes: bytes


def process(salla_file, erp_file, lang):
    """Runs the existing script logic on the uploads. Returns None if a file was rejected."""
    for file, validate in ((salla_file, validate_salla_file), (erp_file, validate_erp_file)):
        try:
            validate(file)
        except InputFileError as error:
            show_file_problem(lang, file, f'error_{error.code}')
            return None

    salla_raw = pd.read_csv(salla_file, header=SALLA_HEADER_ROW)
    salla_file.seek(0)
    salla_cleaned = get_cleaned_salla_data(salla_file)
    _, erp_sticker_numbers = get_cleaned_erp_data(erp_file)

    # Without stickers every product would be reported out of stock, which looks like a real result.
    if not erp_sticker_numbers:
        show_file_problem(lang, erp_file, 'error_no_stickers')
        return None

    out_of_stock = find_out_of_stock_items(salla_cleaned, erp_sticker_numbers)
    return Result(
        total_count=len(salla_raw),
        checked_count=len(salla_cleaned),
        matched_any=len(out_of_stock) < len(salla_cleaned),
        out_of_stock=out_of_stock,
        # The cleaner keeps the original row index, so anything missing from it was skipped.
        skipped=salla_raw.loc[salla_raw.index.difference(salla_cleaned.index)],
        # The BOM makes Excel display the Arabic text correctly.
        csv_bytes=out_of_stock.to_csv(index=False).encode('utf-8-sig'),
    )


def show_file_problem(lang, file, message_key):
    st.error(t(lang, 'file_problem', name=file.name, message=t(lang, message_key)))


def show_result(result, lang):
    st.success(t(lang, 'success', count=len(result.out_of_stock)))

    columns = st.columns(4)
    columns[0].metric(t(lang, 'metric_total'), f'{result.total_count:,}')
    columns[1].metric(t(lang, 'metric_checked'), f'{result.checked_count:,}')
    columns[2].metric(t(lang, 'metric_out_of_stock'), f'{len(result.out_of_stock):,}')
    columns[3].metric(t(lang, 'metric_skipped'), f'{len(result.skipped):,}')

    if not result.matched_any:
        st.warning(t(lang, 'no_match_warning'))

    st.download_button(
        t(lang, 'download'),
        data=result.csv_bytes,
        file_name=f'salla_out_of_stock_{date.today():%Y-%m-%d}.csv',
        mime='text/csv',
        type='primary',
    )

    st.subheader(t(lang, 'preview'))
    st.dataframe(result.out_of_stock, hide_index=True)

    if len(result.skipped):
        st.warning(t(lang, 'skipped_warning', count=len(result.skipped)))
        with st.expander(t(lang, 'skipped_list')):
            st.dataframe(result.skipped, hide_index=True)


st.set_page_config(page_title='Salla Out-of-Stock Checker', page_icon='📦')

lang = st.segmented_control(
    'Language / اللغة',
    options=list(LANGUAGES),
    format_func=LANGUAGES.get,
    default='ar',
    label_visibility='collapsed',
) or 'ar'  # Clicking the active option deselects it, which returns None.

if lang == 'ar':
    st.markdown(RTL_CSS, unsafe_allow_html=True)

st.title(t(lang, 'title'))
st.write(t(lang, 'intro'))
st.markdown(t(lang, 'instructions'))
st.caption(t(lang, 'privacy'))

upload_columns = st.columns(2)
salla_file = upload_columns[0].file_uploader(t(lang, 'salla_label'), type='csv', key='salla_upload')
erp_file = upload_columns[1].file_uploader(t(lang, 'erp_label'), type='csv', key='erp_upload')
if salla_file:
    upload_columns[0].caption(t(lang, 'selected_file', name=salla_file.name))
if erp_file:
    upload_columns[1].caption(t(lang, 'selected_file', name=erp_file.name))

# A result from earlier uploads must not stay on screen next to different files.
upload_ids = (salla_file and salla_file.file_id, erp_file and erp_file.file_id)
if st.session_state.get('upload_ids') != upload_ids:
    st.session_state.upload_ids = upload_ids
    st.session_state.result = None

if st.button(t(lang, 'process'), disabled=not (salla_file and erp_file)):
    st.session_state.result = None
    with st.spinner(t(lang, 'processing')):
        try:
            st.session_state.result = process(salla_file, erp_file, lang)
        except Exception as error:
            st.error(t(lang, 'error_unexpected'))
            with st.expander(t(lang, 'error_details')):
                st.code(f'{type(error).__name__}: {error}')

# Kept in session_state because clicking download reruns this script.
if st.session_state.result is not None:
    show_result(st.session_state.result, lang)
