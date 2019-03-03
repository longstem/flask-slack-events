from flask.signals import Namespace

_signals = Namespace()

request_unauthorized = _signals.signal('slack.request_unauthorized')
expired_event = _signals.signal('slack.expired_event')
invalid_signature = _signals.signal('slack.invalid_signature')
event_received = _signals.signal('slack.event_received')
