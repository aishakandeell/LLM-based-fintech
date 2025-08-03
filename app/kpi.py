import pandas as pd
from io import BytesIO

def extract_kpis(file_bytes, filename, options):
    excel_file = BytesIO(file_bytes)
    xls = pd.ExcelFile(excel_file)
    all_dfs = []

    for sheet in xls.sheet_names:
        df_raw = xls.parse(sheet, header=None)
        df_raw = df_raw.dropna(how='all')

        # Find the row where 'Income Statement' appears
        income_idx = None
        for i, row in df_raw.iterrows():
            if row.astype(str).str.contains("income statement", case=False).any():
                income_idx = i
                break

        if income_idx is None:
            continue

        # Extract from the row after 'Income Statement'
        data_block = df_raw.iloc[income_idx + 1:].copy()

        # Stop at first fully empty row
        empty_rows = data_block.apply(lambda r: r.isna().all(), axis=1)
        if empty_rows.any():
            data_block = data_block.loc[:empty_rows.idxmax() - 1]

        # Use first row as header
        headers = ["KPI"] + list(data_block.iloc[0][1:].astype(str))
        df_cleaned = data_block[1:]
        df_cleaned.columns = headers
        df_cleaned = df_cleaned.reset_index(drop=True)

        all_dfs.append(df_cleaned)

    if not all_dfs:
        raise ValueError("No Income Statement block found in the uploaded file.")

    df_combined = pd.concat(all_dfs, ignore_index=True)
    df_combined = df_combined.loc[:, ~df_combined.columns.duplicated()]
    df_combined = df_combined.fillna("")

    return df_combined
