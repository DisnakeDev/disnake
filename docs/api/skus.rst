.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

SKUs
====

This section documents everything related to SKUs, which represent items being
sold on Discord, like application subscriptions.
See the :ddocs:`official docs <monetization/overview>` for more info.

Discord Models
---------------

SKU
~~~

.. attributetable:: SKU

.. autoclass:: SKU()
    :members:


Data Classes
------------

SKUFlags
~~~~~~~~

.. attributetable:: SKUFlags

.. autoclass:: SKUFlags()
    :members:


Enumerations
------------

SKUType
~~~~~~~

.. class:: SKUType

    Represents the type of an SKU.

    .. versionadded:: 2.10

    .. attribute:: durable

        Represents a durable one-time purchase.

    .. attribute:: consumable

        Represents a consumable one-time purchase.

    .. attribute:: subscription

        Represents a recurring subscription.

    .. attribute:: subscription_group

        Represents a system-generated group for each :attr:`subscription` SKU.
