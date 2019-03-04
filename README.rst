Flask Slack Events
==================

|Pypi| |Build Status| |Codecov| |Code Climate|


`Slack event subscriptions <https://api.slack.com/events-api#subscriptions>`_ for `Flask <http://flask.pocoo.org>`_


Installation
------------

Install last stable version from Pypi::

    pip install flask-slack-events


Create a Slack bot user
-----------------------

See the `Slack's documentation <https://api.slack.com/bot-users#getting-started>`_ for further guidance on creating your bot (**step 1**).

Within the *Basic Information* about your application, copy the **Signing Secret** necessary to `verify requests from Slack <https://api.slack.com/docs/verifying-requests-from-slack>`_.

..  image:: https://user-images.githubusercontent.com/5514990/53696736-cfde0e00-3dfc-11e9-9aeb-23d184f8c600.png
    :alt: Signing Secret


Configure your Application
--------------------------

You should create a ``SlackManager`` object within your application:

.. code-block:: python

    slack_manager = SlackManager()

`Configure your application object <http://flask.pocoo.org/docs/1.0/config/#configuration-basics>`_ updating the ``SLACK_SIGNING_SECRET`` key with the value obtained in the previous **step 1**:

.. code-block:: python

    app.config['SLACK_SIGNING_SECRET'] = '<your Signing Secret>'

Once the actual application object has been created, you can configure it for *SlackManager* object with::

    slack_manager.init_app(app)


Configure your Slack Bot
------------------------

Continue with the `Slacks's documentation <https://api.slack.com/bot-users#setup-events-api>`_ to setting up the Events API (**step 2**) and enter the URL to receive the subscriptions joining your host and the relative path ``/slack/events``:

..  image:: https://user-images.githubusercontent.com/5514990/53696747-e5533800-3dfc-11e9-8cef-4fd13d06e6ef.png
    :alt: Enable Event

Finally, install your bot to a workspace (**step 3**).


How it Works
------------

Now in order to subscribe to `Slack Events <https://api.slack.com/events>`_, use the ``SlackManager.on`` decorator:

.. code-block:: python

    # Reply to only the message events that mention your bot

    @slack_manager.on('app_mention')
    def reply_to_app_mention(sender, data, **extra):
        event = data['event']

        slack_client.api_call(
            'chat.postMessage',
            channel=event['channel'],
            text=f":robot_face: Hello <@{event['user']}>!")


Context Processors
------------------

To inject new variables automatically into the context of a handler, context processors exist in *Flask-Slack-Events*.

A context processor is a function that returns a dictionary:

.. code-block:: python

    @slack_manager.context_processor
    def context_processor(data):
        return dict(my_bot_id='UAZ02BCBH')

The injected variables will be sent as an ``extra`` argument for each event handler ``f(sender, data, **extra)``.


Dispatch Events Asynchronously
------------------------------

Some event handlers can delay the execution of another, to avoid this you can configure the event dispatcher and call handlers asynchronously:

.. code-block:: python

    @slack_manager.dispatch_event_handler
    def async_event_dispatcher(sender, data, handlers, **extra):
        for handler in handlers:
            task(handler)(data, **extra)


Subscribe to Signals
--------------------

The following signals are sended internally by *Flask-Slack-Events*:

signals.request_unauthorized
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Sent when the request received is unauthorized

    Receiver: ``f(sender, **extra)``

signals.expired_event
~~~~~~~~~~~~~~~~~~~~~

    Sent when the event has expired according to the value of ``SLACK_EVENT_EXPIRATION_DELTA`` and the HTTP header ``X-Slack-Request-Timestamp`` received

    Receiver: ``f(sender, **extra)``

signals.invalid_signature
~~~~~~~~~~~~~~~~~~~~~~~~~

    Sent when the signature included within the HTTP header ``X-Slack-Signature`` is invalid

    Receiver: ``f(sender, **extra)``


signals.event_received
~~~~~~~~~~~~~~~~~~~~~~

    Sent when an event has been received

    Receiver: ``f(sender, data, **extra)``


SlackManager Handlers
---------------------

The following handlers are used internally by *Flask-Slack-Events*:

SlackManager.unauthorized_handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Called to handle an unauthorized request

    Handler: ``f()``

    Default: ``SlackManager.unauthorized()``

SlackManager.expired_event_handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Called to handle an expired event

    Handler: ``f()``

    Default: ``SlackManager.expired_event()``

SlackManager.invalid_signature_handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Called to handle a request with an invalid signature

    Handler: ``f()``

    Default: ``SlackManager.invalid_signature()``


SlackManager.dispatch_event_handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Called to dispatch the event to all handlers connected with ``SlackManager.on(event_type)`` decorator

    Handler: ``f(sender, data, handlers, **extra)``

    Default: ``SlackManager.dispatch_event(data)``


Configuration
-------------

The following configuration values are used internally by *Flask-Slack-Events*:

SLACK_SIGNING_SECRET
~~~~~~~~~~~~~~~~~~~~

    Signing Secret to verify whether requests from *Slack* are authentic

    Default: ``''``

SLACK_EVENTS_URL
~~~~~~~~~~~~~~~~

    URL rule that is used to register the *Subscription View*

    Default: ``/slack/events``

SLACK_EVENT_EXPIRATION_DELTA
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Timedelta added to ``time.time()`` to set the expiration time of each event
    If the value is ``None`` then the event never expires

    Default: ``timedelta(seconds=60 * 5)`` (5 minutes)


Marvin the Paranoid Android
---------------------------

`Marvin <https://github.com/longstem/marvin>`_ is a **Slack Bot layout** for *Flask* to develop `Slack Event <https://api.slack.com/events>`_ handlers and deploy on *AWS Lambda* + *API Gateway*


.. |Pypi| image:: https://img.shields.io/pypi/v/flask-slack-events.svg
   :target: https://pypi.python.org/pypi/flask-slack-events
   :alt: Pypi

.. |Build Status| image:: https://travis-ci.org/longstem/flask-slack-events.svg?branch=master
   :target: https://travis-ci.org/longstem/flask-slack-events
   :alt: Build Status

.. |Codecov| image:: https://img.shields.io/codecov/c/github/longstem/flask-slack-events.svg
   :target: https://codecov.io/gh/longstem/flask-slack-events
   :alt: Codecov

.. |Code Climate| image:: https://api.codeclimate.com/v1/badges/c79a185d546f7e34fdd6/maintainability
   :target: https://codeclimate.com/github/longstem/flask-slack-events
   :alt: Codeclimate
