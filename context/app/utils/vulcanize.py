import re
from math import log10

def vulcanize(dataframe):
    """
    Given a dataframe,
    identify the columns for log-fold-change and p-value,
    remove all other columns,
    and replace p-value with its negative log.
    """
    log_fold_col = _pick_col(r'log.*fold.*change', dataframe)
    p_value_col = _pick_col(r'p.*value', dataframe)
    log_p_value_col = '-log10({})'.format(p_value_col)
    dataframe[log_p_value_col] =\
        dataframe[p_value_col].apply(_neg_log)
    return dataframe[[log_fold_col, log_p_value_col]]

def _pick_col(name_re, df):
    match_cols = [
        col for col in df.columns
        if re.search(name_re, col, flags=re.IGNORECASE)
        ]
    assert len(match_cols) == 1
    return match_cols[0]

def _neg_log(x):
    try:
        return -log10(x)
    except ValueError:
        return None