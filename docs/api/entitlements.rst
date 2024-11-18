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

.. autoclass:: EntitlementType()
    :members:

Events
------

- :func:`on_entitlement_create(entitlement) <disnake.on_entitlement_create>`
- :func:`on_entitlement_update(entitlement) <disnake.on_entitlement_update>`
- :func:`on_entitlement_delete(entitlement) <disnake.on_entitlement_delete>`
