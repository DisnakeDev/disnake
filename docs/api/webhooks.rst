.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Webhooks
========

This section documents all objects related to :ddocs:`webhooks <resources/webhook>`,
a low-effort way of sending messages in channels without a user/bot account.

Discord Models
---------------

Webhook
~~~~~~~

.. attributetable:: Webhook

.. autoclass:: Webhook()
    :members:
    :inherited-members:

WebhookMessage
~~~~~~~~~~~~~~

.. attributetable:: WebhookMessage

.. autoclass:: WebhookMessage()
    :members:

SyncWebhook
~~~~~~~~~~~

.. attributetable:: SyncWebhook

.. autoclass:: SyncWebhook()
    :members:
    :inherited-members:

SyncWebhookMessage
~~~~~~~~~~~~~~~~~~

.. attributetable:: SyncWebhookMessage

.. autoclass:: SyncWebhookMessage()
    :members:

PartialWebhookGuild
~~~~~~~~~~~~~~~~~~~

.. attributetable:: PartialWebhookGuild

.. autoclass:: PartialWebhookGuild()
    :members:

PartialWebhookChannel
~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: PartialWebhookChannel

.. autoclass:: PartialWebhookChannel()
    :members:

Enumerations
------------

WebhookType
~~~~~~~~~~~

.. autoclass:: WebhookType()
    :members:

Events
------

- :func:`on_webhooks_update(channel) <disnake.on_webhooks_update>`
