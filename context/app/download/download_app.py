import io

from flask import send_file


class DownloadApp():

    def __init__(self,
                 server=None,
                 url_base_pathname=None,
                 dataframe=None):
        @server.route(url_base_pathname)
        def download():
            return send_file(io.BytesIO(b'TEST'),
                     attachment_filename='data.csv',
                     mimetype='text/csv')