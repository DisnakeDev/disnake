.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Subscriptions
===============

This section documents everything related to Subscription(s), which represents a user making recurring payments for at least one SKU.
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

.. class:: SubscriptionStatus

    Represents the status of a subscription.

    .. versionadded:: 2.10

    .. attribute:: active

        Represents an active Subscription which is scheduled to renew.

    .. attribute:: ending

        Represents an active Subscription which will not renew.

    .. attribute:: inactive

        Represents an inactive Subscription which is not being charged.
