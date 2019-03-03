import time
import unittest
from unittest.mock import Mock, patch

from flask import current_app, url_for

import pytest
from werkzeug.exceptions import Unauthorized

from flask_slack import signals

from .context_managers import catch_signal
from .testcases import JSONTestCase


@pytest.mark.usefixtures('config')
class SlackManagerTestCase(unittest.TestCase):

    def setUp(self):
        self.slack_manager = current_app.slack_manager


class EventTestCase(SlackManagerTestCase):

    def setUp(self):
        super().setUp()
        self.event = {'type': 'test'}


class RouteTests(JSONTestCase, EventTestCase):

    @patch('hmac.compare_digest')
    def test_route(self, compare_digest_mock):
        headers = {
            'X-Slack-Signature': '-',
            'X-Slack-Request-Timestamp': int(time.time()),
        }

        with catch_signal(signals.event_received) as signal_mock:
            response = self.client.post(
                url_for('slack_events'),
                headers=headers,
                json={'event': self.event})

        self.assertEqual(response.status_code, 204)

        compare_digest_mock.assert_called()
        signal_mock.assert_called_with(current_app, event=self.event)


class OnTests(SlackManagerTestCase):

    def test_on(self):
        current_app.slack_manager.on('test')(True)

        handler = self.slack_manager._event_handlers['test'][0]
        self.assertTrue(handler)


class UnauthorizedTests(SlackManagerTestCase):

    def test_unauthorized(self):
        with catch_signal(signals.request_unauthorized) as signal_mock:
            with self.assertRaises(Unauthorized) as http_error:
                self.slack_manager.unauthorized()

        self.assertEqual(http_error.exception.code, 401)
        signal_mock.assert_called_with(current_app)

    def test_unauthorized_handler(self):
        handler_mock = Mock()
        current_app.slack_manager.unauthorized_handler(handler_mock)

        with catch_signal(signals.request_unauthorized) as signal_mock:
            self.slack_manager.unauthorized()

        handler_mock.assert_called_with()
        signal_mock.assert_called_with(current_app)


class ExpiredEventTests(SlackManagerTestCase):

    def test_expired_event(self):
        with catch_signal(signals.expired_event) as signal_mock:
            _, status_code = self.slack_manager.expired_event()

        self.assertEqual(status_code, 403)
        signal_mock.assert_called_with(current_app)

    def test_expired_event_handler(self):
        handler_mock = Mock()
        current_app.slack_manager.expired_event_handler(handler_mock)

        with catch_signal(signals.expired_event) as signal_mock:
            self.slack_manager.expired_event()

        handler_mock.assert_called_with()
        signal_mock.assert_called_with(current_app)


class InvalidSignatureTests(SlackManagerTestCase):

    def test_invalid_signature(self):
        with catch_signal(signals.invalid_signature) as signal_mock:
            _, status_code = self.slack_manager.invalid_signature()

        self.assertEqual(status_code, 403)
        signal_mock.assert_called_with(current_app)

    def test_invalid_signature_handler(self):
        handler_mock = Mock()
        current_app.slack_manager.invalid_signature_handler(handler_mock)

        with catch_signal(signals.invalid_signature) as signal_mock:
            self.slack_manager.invalid_signature()

        handler_mock.assert_called_with()
        signal_mock.assert_called_with(current_app)


class DispatchEventTests(EventTestCase):

    def test_dispatch_event(self):
        handler_mock = Mock()
        current_app.slack_manager.on('test')(handler_mock)

        self.slack_manager.dispatch_event(self.event)

        handler_mock.assert_called_with(current_app, self.event)

    def test_dispatch_event_handler(self):
        handler_mock = Mock()
        current_app.slack_manager.on('test')(handler_mock)

        dispatcher_mock = Mock()
        current_app.slack_manager.dispatch_event_handler(dispatcher_mock)

        self.slack_manager.dispatch_event(self.event)

        handler_mock.assert_not_called()
        dispatcher_mock.assert_called_with(self.event, [handler_mock])
