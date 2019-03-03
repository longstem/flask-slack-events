import time
import unittest
from unittest.mock import patch

import pytest
from werkzeug.exceptions import Unauthorized

from flask_slack import decorators


@pytest.mark.usefixtures('client_class', 'config')
class SlackSignatureRequiredTests(unittest.TestCase):

    @patch('hmac.compare_digest', unsafe=True)
    def test_slack_event_required(self, compare_digest_mock):
        headers = {
            'X-Slack-Signature': '-',
            'X-Slack-Request-Timestamp': int(time.time()),
        }

        self.client.get('/', headers=headers, json={})

        result = decorators.slack_event_required(bool)()

        self.assertFalse(result)
        compare_digest_mock.assert_called()

    def test_unauthorized(self):
        with self.assertRaises(Unauthorized) as http_error:
            decorators.slack_signature_required(bool)()

        self.assertEqual(http_error.exception.code, 401)

    @patch('hmac.compare_digest', unsafe=True)
    def test_expired_event(self, compare_digest_mock):
        headers = {
            'X-Slack-Signature': '-',
            'X-Slack-Request-Timestamp': '0',
        }

        self.client.get('/', headers=headers)

        _, status_code = decorators.slack_signature_required(bool)()

        self.assertEqual(status_code, 403)
        compare_digest_mock.assert_not_called()

    @patch('hmac.compare_digest', unsafe=True, return_value=False)
    def test_invalid_signature(self, compare_digest_mock):
        headers = {
            'X-Slack-Signature': '-',
            'X-Slack-Request-Timestamp': int(time.time()),
        }

        self.client.get('/', headers=headers)

        _, status_code = decorators.slack_signature_required(bool)()

        self.assertEqual(status_code, 403)
        compare_digest_mock.assert_called()


@pytest.mark.usefixtures('client_class')
class SlackChallengeValidationTests(unittest.TestCase):

    def test_slack_challenge_validation(self):
        self.client.post('/', json={'challenge': True})

        result = decorators.slack_challenge_validation(bool)()

        self.assertTrue(result)
