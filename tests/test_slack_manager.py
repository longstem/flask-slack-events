import time
import unittest
from unittest.mock import Mock, patch

from flask import Flask, current_app, url_for

import pytest
from werkzeug.exceptions import Unauthorized

import flask_slack
from flask_slack import signals

from .context_managers import catch_signal


@pytest.mark.usefixtures('config')
class SlackManagerTestCase(unittest.TestCase):

    def setUp(self):
        self.slack_manager = current_app.slack_manager


class EventDataTestCase(SlackManagerTestCase):

    def setUp(self):
        super().setUp()
        self.data = dict(event=dict(type='test'))


class InitTests(unittest.TestCase):

    def test_init(self):
        app = Flask(__name__)
        slack_manager = flask_slack.SlackManager(app)

        self.assertEqual(app.slack_manager, slack_manager)


@pytest.mark.usefixtures('client_class')
class RouteTests(EventDataTestCase):

    @patch('hmac.compare_digest', unsafe=True)
    def test_route(self, compare_digest_mock):
        headers = {
            'X-Slack-Signature': '-',
            'X-Slack-Request-Timestamp': int(time.time()),
        }

        with catch_signal(signals.event_received) as signal_mock:
            response = self.client.post(
                url_for('slack_events'),
                headers=headers,
                json=self.data)

        self.assertEqual(response.status_code, 204)

        compare_digest_mock.assert_called()
        signal_mock.assert_called_once_with(current_app, data=self.data)


class OnTests(SlackManagerTestCase):

    def test_on(self):
        self.slack_manager.on('test')(True)

        handler = self.slack_manager._event_handlers['test'][0]
        self.assertTrue(handler)


class UnauthorizedTests(SlackManagerTestCase):

    def test_unauthorized(self):
        with catch_signal(signals.request_unauthorized) as signal_mock:
            with self.assertRaises(Unauthorized) as http_error:
                self.slack_manager.unauthorized()

        self.assertEqual(http_error.exception.code, 401)
        signal_mock.assert_called_once_with(current_app)

    def test_unauthorized_handler(self):
        handler_mock = Mock()
        self.slack_manager.unauthorized_handler(handler_mock)

        with catch_signal(signals.request_unauthorized) as signal_mock:
            self.slack_manager.unauthorized()

        handler_mock.assert_called_once_with()
        signal_mock.assert_called_once_with(current_app)


class ExpiredEventTests(SlackManagerTestCase):

    def test_expired_event(self):
        with catch_signal(signals.expired_event) as signal_mock:
            _, status_code = self.slack_manager.expired_event()

        self.assertEqual(status_code, 403)
        signal_mock.assert_called_once_with(current_app)

    def test_expired_event_handler(self):
        handler_mock = Mock()
        self.slack_manager.expired_event_handler(handler_mock)

        with catch_signal(signals.expired_event) as signal_mock:
            self.slack_manager.expired_event()

        handler_mock.assert_called_once_with()
        signal_mock.assert_called_once_with(current_app)


class InvalidSignatureTests(SlackManagerTestCase):

    def test_invalid_signature(self):
        with catch_signal(signals.invalid_signature) as signal_mock:
            _, status_code = self.slack_manager.invalid_signature()

        self.assertEqual(status_code, 403)
        signal_mock.assert_called_once_with(current_app)

    def test_invalid_signature_handler(self):
        handler_mock = Mock()
        self.slack_manager.invalid_signature_handler(handler_mock)

        with catch_signal(signals.invalid_signature) as signal_mock:
            self.slack_manager.invalid_signature()

        handler_mock.assert_called_once_with()
        signal_mock.assert_called_once_with(current_app)


class DispatchEventTests(EventDataTestCase):

    def test_dispatch_event(self):
        handler_mock = Mock()

        self.slack_manager.on('test')(handler_mock)
        self.slack_manager.dispatch_event(self.data)

        handler_mock.assert_called_once_with(current_app, self.data)

    def test_dispatch_event_handler(self):
        handler_mock = Mock()
        dispatcher_mock = Mock()

        self.slack_manager.on('test')(handler_mock)
        self.slack_manager.dispatch_event_handler(dispatcher_mock)
        self.slack_manager.dispatch_event(self.data)

        handler_mock.assert_not_called()

        dispatcher_mock.assert_called_once_with(
            current_app, self.data, [handler_mock])
