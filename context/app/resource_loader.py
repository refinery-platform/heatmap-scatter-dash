
import os
from base64 import urlsafe_b64encode

class ResourceLoader():

    def load_resources(self):
        with open(relative_path('extra.css')) as extra_css_file:
            self._css_urls = [
                'https://maxcdn.bootstrapcdn.com/'
                'bootstrap/3.3.7/css/bootstrap.min.css',
                to_data_uri(extra_css_file.read(), 'text/css')
            ]
        with open(relative_path('extra.js')) as extra_js_file:
            self._js_urls = [
                'https://code.jquery.com/'
                'jquery-3.1.1.slim.min.js',
                'https://maxcdn.bootstrapcdn.com/'
                'bootstrap/3.3.7/js/bootstrap.min.js',
                to_data_uri(extra_js_file.read(),
                            'application/javascript')
            ]

        for url in self._css_urls:
            self.app.css.append_css({'external_url': url})

        for url in self._js_urls:
            self.app.scripts.append_script({'external_url': url})

def relative_path(file):
    # https://stackoverflow.com/questions/4060221 for more options
    return os.path.join(os.path.dirname(__file__), file)


def to_data_uri(s, mime):
    uri = (
        ('data:' + mime + ';base64,').encode('utf8') +
        urlsafe_b64encode(s.encode('utf8'))
    ).decode("utf-8", "strict")
    return uri