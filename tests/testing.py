import json

from flask.testing import FlaskClient


class JSONTestClient(FlaskClient):

    def open(self, *args, **kwargs):
        if 'json' in kwargs:
            kwargs['data'] = json.dumps(kwargs.pop('json'))
            kwargs['content_type'] = 'application/json'
        return super().open(*args, **kwargs)
