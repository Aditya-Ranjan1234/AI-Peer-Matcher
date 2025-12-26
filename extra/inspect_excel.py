import pandas as pd
import os

file_path = r"D:\5th Sem\peer matcher\3rd Sem CS CY & CD 2024 Student list with Batches.xlsx"

try:
    xl = pd.ExcelFile(file_path)
    with open('excel_info.txt', 'w', encoding='utf-8') as f:
        f.write(f"Sheet names: {xl.sheet_names}\n")
        for sheet in xl.sheet_names:
            f.write(f"\n--- Sheet: {sheet} ---\n")
            df = xl.parse(sheet)
            f.write(f"Columns: {list(df.columns)}\n")
            f.write(df.head(10).to_string())
            f.write("\n" + "-" * 20 + "\n")
    print("Done writing to excel_info.txt")
except Exception as e:
    print(f"Error: {e}")
