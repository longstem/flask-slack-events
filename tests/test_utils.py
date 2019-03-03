import time
import unittest
from unittest.mock import patch

from flask import current_app

import pytest
from werkzeug.exceptions import Unauthorized

from flask_slack import utils


@pytest.mark.usefixtures('client_class')
class GetHTTPHeaderTests(unittest.TestCase):

    def test_get_http_header(self):
        self.client.get('/', headers={'test': True})
        self.assertTrue(utils.get_http_header('test'))

    def test_get_http_header_unauthorized(self):
        with self.assertRaises(Unauthorized) as http_error:
            utils.get_http_header('test')

        self.assertEqual(http_error.exception.code, 401)


@pytest.mark.usefixtures('config')
class EventHasExpiredTests(unittest.TestCase):

    def test_event_has_expired(self):
        timestamp = time.time() - current_app.slack_manager\
            .default_event_expiration.total_seconds()

        self.assertTrue(utils.event_has_expired(timestamp))

    def test_event_has_not_expired(self):
        timestamp = time.time()
        self.assertFalse(utils.event_has_expired(timestamp))

    def test_expiration_disabled(self):
        timestamp = time.time() - current_app.slack_manager\
            .default_event_expiration.total_seconds()

        current_app.config['SLACK_EVENT_EXPIRATION_DELTA'] = None
        self.assertFalse(utils.event_has_expired(timestamp))


@pytest.mark.usefixtures('config')
class CompareSignatureTests(unittest.TestCase):

    @patch('hmac.compare_digest', unsafe=True)
    def test_compare_signatured(self, compare_digest_mock):
        utils.compare_signature('-', '-')
        compare_digest_mock.assert_called()
