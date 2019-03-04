from collections import defaultdict
from datetime import timedelta

from flask import abort, current_app, request

from . import errors, signals
from .decorators import slack_event_required


class SlackManager:

    def __init__(self, app=None):
        self.unauthorized_callback = None
        self.expired_event_callback = None
        self.invalid_signature_callback = None
        self.dispatch_event_callback = None

        self._context_processors = []
        self._event_handlers = defaultdict(list)

        self.default_event_expiration = timedelta(seconds=60 * 5)

        if app is not None:
            self.init_app(app)

    @slack_event_required
    def _view_func(self, *args, **kwargs):
        data = request.get_json()
        current_app_object = current_app._get_current_object()

        signals.event_received.send(current_app_object, data=data)
        self.dispatch_event(data)
        return '', 204

    def init_app(self, app, blueprint=None):
        app.slack_manager = self
        url_rule = app.config.get('SLACK_EVENTS_URL', '/slack/events')

        (blueprint or app).add_url_rule(
            url_rule,
            endpoint='slack_events',
            view_func=self._view_func,
            methods=['POST'])

    def on(self, event_type):
        def decorator(f):
            self._event_handlers[event_type].append(f)
            return f
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

    def context_processor(self, f):
        self._context_processors.append(f)
        return f

    def get_context(self, data):
        context = {}
        for processor in self._context_processors:
            context.update(processor(data))
        return context

    def dispatch_event(self, data):
        sender = current_app._get_current_object()
        handlers = self._event_handlers[data['event']['type']]
        context = self.get_context(data)

        if self.dispatch_event_callback is not None:
            self.dispatch_event_callback(sender, data, handlers, **context)
        else:
            for handler in handlers:
                handler(sender, data, **context)

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
