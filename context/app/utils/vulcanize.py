import re
from math import log10


class Vulcanizer():

    def __init__(self, log_fold_re_list, p_value_re_list):
        self.log_fold_re_list = log_fold_re_list
        self.p_value_re_list = p_value_re_list


    def vulcanize(self, dataframe):
        """
        Given a dataframe,
        identify the columns for log-fold-change and p-value,
        remove all other columns,
        and replace p-value with its negative log.
        """
        log_fold_col = self._pick_log_fold(dataframe)
        p_value_col = self._pick_p_value(dataframe)
        log_p_value_col = '-log10({})'.format(p_value_col)
        dataframe[log_p_value_col] =\
            dataframe[p_value_col].apply(_neg_log)
        two_columns = dataframe[[log_fold_col, log_p_value_col]]
        return two_columns.dropna(axis='rows', how='all')
        # Plotly fails to show anything if rows with missing data are present,
        # (I think.)

    def _pick_log_fold(self, dataframe):
        return _pick_col(self.log_fold_re_list, dataframe)

    def _pick_p_value(self, dataframe):
        return _pick_col(self.p_value_re_list, dataframe)


def _pick_col(name_re_list, df):
    for name_re in name_re_list:
        match_cols = [
            col for col in df.columns
            if re.search(name_re, col, flags=re.IGNORECASE)
        ]
        if len(match_cols) == 1:
            break
    else:
        raise Exception('expected one match for {} in {}'.format(
            name_re_list, df.columns.tolist()))
    return match_cols[0]


def _neg_log(x):
    try:
        return -log10(x)
    except ValueError:
        return None
