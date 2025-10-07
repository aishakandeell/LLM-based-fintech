import pandas as pd
from io import BytesIO
from datetime import datetime

BALANCE_SHEET_KPIS = [
    "Total Cash",
    "Marketable Securities",
    "Accounts Receivable",
    "Inventories",
    "Other Current Assets",
    "Total Current Assets",
    "Net Fixed Assets",
    "Total Assets",
    "Short Term Debt",
    "Accounts Payable",
    "Due To HCs & Affiliates",
]
#helper functions
def _load_sheet(file_bytes, sheet_index=0):
    # Reads the Excel file from raw bytes and returns the DataFrame for the chosen sheet.
    # Input: file_bytes (Excel file in memory), sheet_index (which sheet to load, default first).
    # Output: Pandas DataFrame with the full sheet (no headers).
    xls = pd.ExcelFile(BytesIO(file_bytes))
    return xls.parse(xls.sheet_names[sheet_index], header=None)

def _find_header_row(df, title):
    # Finds the row index in the sheet where the given title (e.g., "Balance Sheet") appears in column 1.
    # Input: df (DataFrame of the sheet), title (string to search for).
    # Output: integer row index if found; raises ValueError if not found.
    idx = df.index[df.iloc[:, 1].astype(str).str.contains(title, case=False, na=False)]
    if len(idx) == 0:
        raise ValueError(f"{title} header not found.")
    return int(idx[0])

def _year_columns_from_header_row(df, header_row, start_col=3):
    # Extracts all year labels (like 2020, 2021, …) from the header row, starting from column 3.
    # Input: df (sheet DataFrame), header_row (row index where the statement starts), start_col (first date column).
    # Output: 
    #   - years: list of integer years,
    #   - col_map: dictionary mapping year → column index in the DataFrame.
    date_cells = df.iloc[header_row, start_col:].dropna()
    periods = pd.to_datetime(date_cells, errors="coerce").dropna()
    years = periods.dt.year.tolist()
    col_map = {yr: (start_col + i) for i, yr in enumerate(years)}
    return years, col_map

def _find_row_for_label(df, label):
    # Finds which row a KPI label (e.g., "Total Cash") is on.
    # Input: df (sheet DataFrame), label (string to match).
    # Output: row index (int) if found, else None.
    # Tries exact match first, then fuzzy 'contains' search.
    exact = df.index[df.iloc[:,1].astype(str).str.fullmatch(label, case=False, na=False)]
    if len(exact): return int(exact[0])
    fuzzy = df.index[df.iloc[:,1].astype(str).str.contains(label, case=False, na=False)]
    if len(fuzzy): return int(fuzzy[0])
    return None

def _build_matrix(df, kpi_labels, row_map, wanted_years, col_map):
     # Builds a tidy DataFrame of KPI values across years.
    data = {"Year": wanted_years}
    for k in kpi_labels:
        r = row_map.get(k)
        if r is None:
            data[k] = [None] * len(wanted_years)
        else:
            vals = []
            for y in wanted_years:
                c = col_map[y]
                v = df.iat[r, c]
                try:
                    vals.append(float(v))
                except Exception:
                    vals.append(None)
            data[k] = vals
    return pd.DataFrame(data)

def extract_balance_sheet_kpis(file_bytes, years_wanted=(2020, 2021, 2022, 2023, 2024)):
    df = _load_sheet(file_bytes, sheet_index=0)
    bs_row = _find_header_row(df, "Balance Sheet")
    _, col_map = _year_columns_from_header_row(df, bs_row, start_col=3)

    wanted_years = [y for y in years_wanted if y in col_map]

    row_map = {k: _find_row_for_label(df, k) for k in BALANCE_SHEET_KPIS}
    return _build_matrix(df, BALANCE_SHEET_KPIS, row_map, wanted_years, col_map)

#old 
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
