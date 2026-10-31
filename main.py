from pathlib import Path

import pandas as pd

def get_cleaned_salla_data(file_path):
    """Reads Salla CSV, cleans SKU numbers, and returns a DataFrame with a 'cleaned_sku_number' column.
       Rows with non-numeric or missing cleaned SKUs are dropped."""
    salla_df = pd.read_csv(file_path, header=1)
    salla_df_copy = salla_df.copy()
    salla_df_copy['extracted_sku_part'] = salla_df_copy['sku_number'].astype(str).str.split('-').str[-1]
    salla_df_copy['cleaned_sku_number'] = pd.to_numeric(salla_df_copy['extracted_sku_part'], errors='coerce')
    salla_df_copy.dropna(subset=['cleaned_sku_number'], inplace=True)
    salla_df_copy['cleaned_sku_number'] = salla_df_copy['cleaned_sku_number'].astype(int)
    salla_df_copy.drop(columns=['extracted_sku_part'], inplace=True)
    return salla_df_copy

def get_cleaned_erp_data(file_path):
    """Reads ERP CSV, cleans sticker numbers, and returns a DataFrame with 'sticker_number' cleaned and a set of unique sticker numbers."""
    erp_df = pd.read_csv(file_path)
    erp_df.columns = erp_df.columns.str.strip()
    erp_df['sticker_number'] = pd.to_numeric(erp_df['sticker_number'], errors='coerce')
    erp_df.dropna(subset=['sticker_number'], inplace=True)
    erp_df['sticker_number'] = erp_df['sticker_number'].astype(int)
    erp_sticker_numbers_set = set(erp_df['sticker_number'].unique())
    return erp_df, erp_sticker_numbers_set


def find_out_of_stock_items(salla_df, erp_sticker_numbers_set):
    """Returns the Salla rows whose cleaned SKU does not appear in the ERP sticker numbers."""
    return salla_df[~salla_df['cleaned_sku_number'].isin(erp_sticker_numbers_set)]


DATA_DIR = Path(__file__).parent / 'data'
SALLA_ORIGINAL_PATH = DATA_DIR / 'marketing-internal-data - Salla Product Quantities Sheet.csv'
ERP_ORIGINAL_PATH = DATA_DIR / 'marketing-internal-data - متابعة الملصقات  الموجودة فى م.csv'
OUT_OF_STOCK_SALLA_OUTPUT_PATH = DATA_DIR / 'salla_out_of_stock_new.csv'


if __name__ == '__main__':
    # 1. Get cleaned Salla data with a 'cleaned_sku_number' column
    salla_df_processed = get_cleaned_salla_data(SALLA_ORIGINAL_PATH)
    print(f"Processed Salla file has {len(salla_df_processed)} rows after cleaning SKUs.")

    # 2. Get cleaned ERP data and its unique sticker numbers
    erp_df_full_cleaned, erp_sticker_numbers_set = get_cleaned_erp_data(ERP_ORIGINAL_PATH)
    print(f"Full cleaned ERP file has {len(erp_df_full_cleaned)} rows.")

    # 3. Identify Salla items that are 'out of stock' based on ERP file
    out_of_stock_salla_df = find_out_of_stock_items(salla_df_processed, erp_sticker_numbers_set)

    # 4. Save the out-of-stock Salla items to a new CSV
    out_of_stock_salla_df.to_csv(OUT_OF_STOCK_SALLA_OUTPUT_PATH, index=False)
    print(f"\nOut of stock Salla items saved successfully to: {OUT_OF_STOCK_SALLA_OUTPUT_PATH}")
    print(f"Total out of stock Salla items: {len(out_of_stock_salla_df)}")
