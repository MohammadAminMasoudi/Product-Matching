import re
import string
import pandas as pd
import numpy as np

def clean_text(text: str) -> str:
    \"\"\"Basic text cleaning:
    - lowercasing
    - strip HTML
    - remove non-ASCII
    - remove punctuation
    - collapse whitespace
    \"\"\"
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"<.*?>", " ", text)
    text = text.encode("ascii", errors="ignore").decode()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text

def normalize_price(price) -> float:
    \"\"\"Extract a numeric price from a string; return NaN if not possible.\"\"\"
    try:
        return float(re.sub(r"[^0-9.]", "", str(price)))
    except Exception:
        return np.nan

def normalize_category(cat: str) -> str:
    \"\"\"Normalize hierarchical category: lowercased and joined with ' > '.\"\"\"
    if pd.isna(cat):
        return ""
    return " > ".join([c.strip().lower() for c in str(cat).split(">")])

def ensure_str(x) -> str:
    return "" if pd.isna(x) else str(x)