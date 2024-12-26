.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Entitlements
============

This section documents everything related to entitlements, which represent access to :doc:`skus`.

Discord Models
---------------

Entitlement
~~~~~~~~~~~

.. attributetable:: Entitlement

.. autoclass:: Entitlement()
    :members:


Enumerations
------------

EntitlementType
~~~~~~~~~~~~~~~

.. class:: EntitlementType

    Represents the type of an entitlement.

    .. versionadded:: 2.10

    .. attribute:: purchase

        Represents an entitlement purchased by a user.

    .. attribute:: premium_subscription

        Represents an entitlement for a Discord Nitro subscription.

    .. attribute:: developer_gift

        Represents an entitlement gifted by the application developer.

    .. attribute:: test_mode_purchase

        Represents an entitlement purchased by a developer in application test mode.

    .. attribute:: free_purchase

        Represents an entitlement granted when the SKU was free.

    .. attribute:: user_gift

        Represents an entitlement gifted by another user.

    .. attribute:: premium_purchase

        Represents an entitlement claimed by a user for free as a Discord Nitro subscriber.

    .. attribute:: application_subscription

        Represents an entitlement for an application subscription.

Events
------

- :func:`on_entitlement_create(entitlement) <disnake.on_entitlement_create>`
- :func:`on_entitlement_update(entitlement) <disnake.on_entitlement_update>`
- :func:`on_entitlement_delete(entitlement) <disnake.on_entitlement_delete>`
