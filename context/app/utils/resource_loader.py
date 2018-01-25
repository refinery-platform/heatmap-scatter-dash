import os

def relative_path(base, file):
    # https://stackoverflow.com/questions/4060221 for more options
    return os.path.join(os.path.dirname(base), file)

class ResourceLoader():

    def load_resources(self):
        self._css_urls = [
            'https://maxcdn.bootstrapcdn.com/'
            'bootstrap/3.3.7/css/bootstrap.min.css',
            '/static/extra.css'
        ]
        self._js_urls = [
            'https://code.jquery.com/'
            'jquery-3.1.1.slim.min.js',
            'https://maxcdn.bootstrapcdn.com/'
            'bootstrap/3.3.7/js/bootstrap.min.js',
            '/static/extra.js'
        ]

        for url in self._css_urls:
            self.app.css.append_css({'external_url': url})

        for url in self._js_urls:
            self.app.scripts.append_script({'external_url': url})
