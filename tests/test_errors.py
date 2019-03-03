import unittest

import pytest

from flask_slack import errors


@pytest.mark.usefixtures('client_class')
class ForbiddenTests(unittest.TestCase):

    def test_forbidden(self):
        response, status_code = errors.forbidden('test')

        self.assertEqual(status_code, 403)
        self.assertEqual(response.json['message'], 'test')
