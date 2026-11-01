import pandas as pd
from src.config import IDENTIFIER_COLUMNS
def safe_csv(frame: pd.DataFrame) -> bytes:
    out=frame.drop(columns=[c for c in IDENTIFIER_COLUMNS if c in frame],errors="ignore").copy()
    for col in out.select_dtypes(include="object"):
        out[col]=out[col].map(lambda v: "'"+v if isinstance(v,str) and v[:1] in "=+-@\t\r" else v)
    return out.to_csv(index=False).encode("utf-8")
