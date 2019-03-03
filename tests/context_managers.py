from contextlib import contextmanager
from unittest.mock import Mock

from flask import current_app


@contextmanager
def catch_signal(signal):
    handler = Mock(spec=bool)
    signal.connect_via(current_app._get_current_object())(handler)
    yield handler
    signal.disconnect(handler)
