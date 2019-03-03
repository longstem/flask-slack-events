from flask import Flask

import pytest

from flask_slack import SlackManager


@pytest.fixture
def app():
    app = Flask(__name__)
    slack_manager = SlackManager()
    slack_manager.init_app(app)
    return app
