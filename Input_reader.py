import pandas as pd
import os

def read_keywords(filepath):
    ext = os.path.splitext(filepath)[-1].lower()
    if ext == ".csv":
        df = pd.read_csv(filepath, header=None)
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(filepath, header=None)
    else:
        raise ValueError("Unsupported file type")
    return df.iloc[:, 0].dropna().astype(str).tolist() 
