from collections import defaultdict
from datetime import timedelta
from functools import wraps

from flask import abort, current_app, request

from . import errors, signals
from .decorators import slack_event_required


class SlackManager:

    def __init__(self, app=None):
        self.unauthorized_callback = None
        self.expired_event_callback = None
        self.invalid_signature_callback = None
        self.dispatch_event_callback = None

        self.default_event_expiration = timedelta(seconds=60 * 5)

        self._event_handlers = defaultdict(list)

        if app is not None:
            self.init_app(app)

    @slack_event_required
    def _view_func(self, *args, **kwargs):
        event = request.get_json()['event']
        current_app_object = current_app._get_current_object()

        signals.event_received.send(current_app_object, event=event)
        self.dispatch_event(event)
        return '', 204

    def init_app(self, app, blueprint=None):
        app.slack_manager = self
        route_url = app.config.get('SLACK_EVENTS_URL', '/slack/events')

        (blueprint or app).add_url_rule(
            route_url,
            endpoint='slack_events',
            view_func=self._view_func,
            methods=['POST'])

    def on(self, event_type):
        def decorator(f):
            self._event_handlers[event_type].append(f)

            @wraps(f)
            def decorated_handler(*args, **kwargs):
                f(*args, **kwargs)
            return decorated_handler
        return decorator

    def unauthorized(self):
        signals.request_unauthorized.send(current_app._get_current_object())

        if self.unauthorized_callback is not None:
            return self.unauthorized_callback()

        abort(401)

    def expired_event(self):
        signals.expired_event.send(current_app._get_current_object())

        if self.expired_event_callback is not None:
            return self.expired_event_callback()
        return errors.forbidden('Event has expired')

    def invalid_signature(self):
        signals.invalid_signature.send(current_app._get_current_object())

        if self.invalid_signature_callback is not None:
            return self.invalid_signature_callback()
        return errors.forbidden('Invalid signature')

    def dispatch_event(self, event):
        handlers = current_app.slack_manager._event_handlers[event['type']]

        if self.dispatch_event_callback is not None:
            self.dispatch_event_callback(event, handlers)
        else:
            for handler in handlers:
                handler(current_app._get_current_object(), event)

    def unauthorized_handler(self, callback):
        self.unauthorized_callback = callback
        return callback

    def expired_event_handler(self, callback):
        self.expired_event_callback = callback
        return callback

    def invalid_signature_handler(self, callback):
        self.invalid_signature_callback = callback
        return callback

    def dispatch_event_handler(self, callback):
        self.dispatch_event_callback = callback
        return callback
