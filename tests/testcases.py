import json
import unittest

import pytest


@pytest.mark.usefixtures('client_class')
class JSONTestCase(unittest.TestCase):

    def open(self, *args, **kwargs):
        if 'json' in kwargs:
            kwargs['data'] = json.dumps(kwargs.pop('json'))
            kwargs['content_type'] = 'application/json'
        return super().open(*args, **kwargs)
