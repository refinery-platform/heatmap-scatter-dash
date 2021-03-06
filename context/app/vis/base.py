import dash
import pandas

from app.utils.frames import center_and_scale_rows
from app.utils.pca import pca
from app.utils.search import SimpleIndex


class VisBase():

    def __init__(self,
                 union_dataframe,
                 union_label_map=None,
                 diff_dataframes={'none given': pandas.DataFrame()},
                 meta_dataframe=None,
                 most_variable_rows=500,
                 api_prefix=None,
                 debug=False,
                 server=None,
                 url_base_pathname=None,
                 html_table=False,
                 truncate_table=None):
        self._most_variable_rows = most_variable_rows

        self._union_dataframe = union_dataframe
        self._union_label_map = union_label_map or {
            i: i for i in union_dataframe.index}
        self._pca_dataframe = pca(self._union_dataframe)
        self._scaled_dataframe = center_and_scale_rows(self._union_dataframe)
        self._diff_dataframes = diff_dataframes
        self._meta_dataframe = meta_dataframe

        self._conditions = self._union_dataframe.axes[1].tolist()
        self._genes = self._union_dataframe.axes[0].tolist()
        self._metas = self._meta_dataframe.axes[1].tolist()

        self._genes_index = SimpleIndex()
        for (gene, label) in self._union_label_map.items():
            self._genes_index.add_document(gene, label)
        self._debug = debug
        self._html_table = html_table
        self._truncate_table = truncate_table
        self.app = dash.Dash(server=server,
                             url_base_pathname=url_base_pathname)
        if api_prefix:
            self.app.config.update({
                'requests_pathname_prefix': api_prefix
            })
        self.app.title = 'Heatmap + Scatterplots'
        # Works, but not officially supported:
        # https://community.plot.ly/t/including-page-titles-favicon-etc-in-dash-app/4648

    # TODO: Remove?
    # def info(self, *fields):
    #     if self._debug:
    #         # TODO: logging.info() didn't work. Check logging levels?
    #         print(' | '.join([str(field) for field in fields]))
