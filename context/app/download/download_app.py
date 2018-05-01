import io

from flask import send_file, make_response


class DownloadApp():

    def __init__(self,
                 server=None,
                 url_base_pathname=None,
                 dataframe=None):
        @server.route(url_base_pathname)
        def download():
            # TODO: Stream it, rather than holding the whole thing in memory.
            # http://flask.pocoo.org/docs/1.0/patterns/streaming/

            response = make_response(dataframe.to_csv())
            response.headers.set('Content-Type', 'text/csv')
            response.headers.set(
                'Content-Disposition', 'attachment', filename='data.csv')
            return response
