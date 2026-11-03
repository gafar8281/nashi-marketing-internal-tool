from pathlib import Path
import pandas as pd

AVAILABLE_QUANTITY_COLUMN = 'available_quantity'


def read_salla_file(file_path):
    """Reads the Salla CSV as text, so every value can be written back exactly as it was read."""
    return pd.read_csv(file_path, dtype=str, keep_default_na=False)


def get_cleaned_erp_data(file_path):
    """Reads ERP CSV, cleans sticker numbers, and returns a DataFrame with 'sticker_number' cleaned and a set of unique sticker numbers."""
    erp_df = pd.read_csv(file_path)
    erp_df.columns = erp_df.columns.str.strip()
    erp_df['sticker_number'] = pd.to_numeric(erp_df['sticker_number'], errors='coerce')
    erp_df.dropna(subset=['sticker_number'], inplace=True)
    erp_df['sticker_number'] = erp_df['sticker_number'].astype(int)
    erp_sticker_numbers_set = set(erp_df['sticker_number'].unique())
    return erp_df, erp_sticker_numbers_set


def update_available_quantity(salla_df, erp_sticker_numbers_set):
    """Returns a copy of the Salla rows with available_quantity set, plus the in-stock and out-of-stock counts.

    A product is in stock (1) if the number after the last '-' in its SKU is in the ERP,
    otherwise out of stock (0). Rows whose SKU has no usable number keep their existing value.
    """
    extracted_sku_part = salla_df['sku_number'].str.split('-').str[-1]
    sku_numbers = pd.to_numeric(extracted_sku_part, errors='coerce').dropna().astype(int)
    in_stock = sku_numbers.isin(erp_sticker_numbers_set)

    updated_df = salla_df.copy()
    updated_df.loc[in_stock.index, AVAILABLE_QUANTITY_COLUMN] = in_stock.map({True: '1', False: '0'})
    in_stock_count = int(in_stock.sum())
    return updated_df, in_stock_count, len(in_stock) - in_stock_count


def salla_csv_bytes(salla_df):
    """Returns the Salla rows as CSV bytes. The BOM makes Excel display the Arabic product data correctly."""
    return salla_df.to_csv(index=False).encode('utf-8-sig')


DATA_DIR = Path(__file__).parent / 'data'
SALLA_ORIGINAL_PATH = DATA_DIR / 'marketing-internal-data - Salla Product Quantities Sheet.csv'
ERP_ORIGINAL_PATH = DATA_DIR / 'marketing-internal-data - متابعة الملصقات  الموجودة فى م.csv'


if __name__ == '__main__':
    # 1. Read the Salla file without changing any of its values
    salla_df = read_salla_file(SALLA_ORIGINAL_PATH)
    print(f"Salla file has {len(salla_df)} rows.")

    # 2. Get cleaned ERP data and its unique sticker numbers
    erp_df_full_cleaned, erp_sticker_numbers_set = get_cleaned_erp_data(ERP_ORIGINAL_PATH)
    print(f"Full cleaned ERP file has {len(erp_df_full_cleaned)} rows.")

    # 3. Set available_quantity from the ERP file
    updated_salla_df, in_stock_count, out_of_stock_count = update_available_quantity(
        salla_df, erp_sticker_numbers_set
    )

    # 4. Save over the original Salla file
    SALLA_ORIGINAL_PATH.write_bytes(salla_csv_bytes(updated_salla_df))
    print(f"\nSalla file updated: {SALLA_ORIGINAL_PATH}")
    print(f"In stock: {in_stock_count}, out of stock: {out_of_stock_count}")
    print(f"Not checked, left unchanged: {len(salla_df) - in_stock_count - out_of_stock_count}")
