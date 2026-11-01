from __future__ import annotations
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from src.config import ASSOCIATION_COLUMNS

def encode_transactions(frame: pd.DataFrame, max_categories: int=60) -> pd.DataFrame:
    cols=[]
    for col in ASSOCIATION_COLUMNS:
        if col not in frame: continue
        values=frame[col].fillna("Missing").astype(str)
        allowed=values.value_counts().head(max_categories).index
        cols.append(pd.get_dummies(values.where(values.isin(allowed), "Other"), prefix=col, prefix_sep="="))
    if not cols: return pd.DataFrame()
    return pd.concat(cols,axis=1).astype(bool)

def run_apriori(frame: pd.DataFrame, min_support=.02, min_confidence=.30, min_lift=1.0, max_rows=50000) -> tuple[pd.DataFrame,pd.DataFrame,int]:
    if not .001 <= min_support <= .2: raise ValueError("Minimum support must be between 0.001 and 0.20.")
    source=frame.sample(max_rows,random_state=42) if len(frame)>max_rows else frame
    matrix=encode_transactions(source)
    if matrix.empty: return pd.DataFrame(),pd.DataFrame(),len(source)
    itemsets=apriori(matrix,min_support=min_support,use_colnames=True)
    if itemsets.empty: return itemsets,pd.DataFrame(),len(source)
    rules=association_rules(itemsets,metric="confidence",min_threshold=min_confidence)
    if rules.empty: return itemsets,rules,len(source)
    rules=rules[rules["lift"]>=min_lift].copy()
    for col in ["antecedents","consequents"]: rules[col]=rules[col].apply(lambda x:" • ".join(sorted(x)))
    return itemsets.sort_values("support",ascending=False),rules.sort_values(["lift","confidence"],ascending=False),len(source)
