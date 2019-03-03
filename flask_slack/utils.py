import hashlib
import hmac
import time

from flask import current_app, request


def get_http_header(name):
    value = request.headers.get(name)

    if not value:
        return current_app.slack_manager.unauthorized()
    return value


def event_has_expired(timestamp):
    expiration = current_app.config.get(
        'SLACK_EVENT_EXPIRATION_DELTA',
        current_app.slack_manager.default_event_expiration)

    if expiration is None:
        return False

    return (time.time() - int(timestamp)) > expiration.total_seconds()


def compare_signature(slack_signature, timestamp):
    sig_basestring = ('v0:' + timestamp + ':').encode() + request.get_data()
    signing_secret = current_app.config.get('SLACK_SIGNING_SECRET', '')

    signature = 'v0=' + hmac.new(
        signing_secret.encode(),
        msg=sig_basestring,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(signature, slack_signature)
