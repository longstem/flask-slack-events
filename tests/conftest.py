from flask import Flask

import pytest

from flask_slack import SlackManager

from .testing import JSONTestClient


@pytest.fixture
def app():
    app = Flask(__name__)
    slack_manager = SlackManager()
    slack_manager.init_app(app)
    app.test_client_class = JSONTestClient
    return app
