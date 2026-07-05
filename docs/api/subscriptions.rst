.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Subscriptions
=============

This section documents everything related to subscriptions, which represent a user making recurring payments for at least one SKU.
See the :ddocs:`official docs <monetization/overview>` for more info.

Discord Models
--------------

Subscription
~~~~~~~~~~~~

.. attributetable:: Subscription

.. autoclass:: Subscription()
    :members:

Enumerations
------------

SubscriptionStatus
~~~~~~~~~~~~~~~~~~

.. autoclass:: SubscriptionStatus()
    :members:

Events
------

- :func:`on_subscription_create(subscription) <disnake.on_subscription_create>`
- :func:`on_subscription_update(subscription) <disnake.on_subscription_update>`
- :func:`on_subscription_delete(subscription) <disnake.on_subscription_delete>`
