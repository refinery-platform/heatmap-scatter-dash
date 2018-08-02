import re
from math import log10

LOG_FOLD_RE = r'\blog[^a-z]'
P_VALUE_RE = r'p.*value'


def vulcanize(dataframe):
    """
    Given a dataframe,
    identify the columns for log-fold-change and p-value,
    remove all other columns,
    and replace p-value with its negative log.
    """
    log_fold_col = _pick_col(LOG_FOLD_RE, dataframe)
    p_value_col = _pick_col(P_VALUE_RE, dataframe)
    log_p_value_col = '-log10({})'.format(p_value_col)
    dataframe[log_p_value_col] =\
        dataframe[p_value_col].apply(_neg_log)
    two_columns = dataframe[[log_fold_col, log_p_value_col]]
    return two_columns.dropna(axis='rows', how='all')
    # Plotly fails to show anything if rows with missing data are present,
    # (I think.)


def _pick_col(name_re, df):
    match_cols = [
        col for col in df.columns
        if re.search(name_re, col, flags=re.IGNORECASE)
    ]
    assert len(match_cols) == 1, \
        'expected one match for /{}/i in {}, got {}'.format(
            name_re, df.columns.tolist(), match_cols
    )
    return match_cols[0]


def _neg_log(x):
    try:
        return -log10(x)
    except ValueError:
        return None
