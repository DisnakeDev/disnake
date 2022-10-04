.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Roles
=====

This section documents everything related to roles - a way of granting (or limiting) access to certain information/actions
for a group of people.

Classes
-------

Role
~~~~

.. attributetable:: Role

.. autoclass:: Role()
    :members:

Data Classes
------------

RoleTags
~~~~~~~~

.. attributetable:: RoleTags

.. autoclass:: RoleTags()
    :members:

Events
------

- :func:`disnake.on_guild_role_create(role)`
- :func:`disnake.on_guild_role_delete(role)`
- :func:`disnake.on_guild_role_update(before, after)`

See all :ref:`related events <related_events_role>`!
