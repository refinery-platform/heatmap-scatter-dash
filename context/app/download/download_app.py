import json

from flask import make_response, request


class DownloadApp():
    '''
    Trivial Flask app that provides CSV download of selected data points.
    '''

    def __init__(self,
                 server=None,
                 url_base_pathname=None,
                 dataframe=None):
        @server.route(url_base_pathname, methods=['POST'])
        def download():
            # TODO: Stream it, rather than holding the whole thing in memory.
            # http://flask.pocoo.org/docs/1.0/patterns/streaming/
            # ... but only if we actually see a problem.

            # TODO: Include the metadata rows.

            conditions = json.loads(request.form['conditions-json'])
            genes = json.loads(request.form['genes-json'])

            filtered_df = dataframe.reindex(genes)[conditions]

            response = make_response(filtered_df.to_csv())
            response.headers.set('Content-Type', 'text/csv')
            response.headers.set(
                'Content-Disposition', 'attachment', filename='data.csv')
            return response
