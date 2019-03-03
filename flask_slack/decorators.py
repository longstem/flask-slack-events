from functools import wraps

from flask import current_app, request

from .utils import compare_signature, event_has_expired, get_http_header

__all__ = ['slack_event_required']


def slack_signature_required(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        timestamp = get_http_header('X-Slack-Request-Timestamp')

        if event_has_expired(timestamp):
            return current_app.slack_manager.expired_event()

        slack_signature = get_http_header('X-Slack-Signature')

        if not compare_signature(slack_signature, timestamp):
            return current_app.slack_manager.invalid_signature()

        return f(*args, **kwargs)
    return decorated_view


def slack_challenge_validation(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        data = request.get_json()
        return data.get('challenge') or f(*args, **kwargs)
    return decorated_view


def slack_event_required(f):
    return slack_signature_required(slack_challenge_validation(f))
