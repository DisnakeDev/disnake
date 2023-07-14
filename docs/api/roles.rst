.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Roles
=====

This section documents everything related to roles - a way of granting (or limiting) access to certain information/actions for a group of users.

Discord Models
---------------

Role
~~~~

.. attributetable:: Role

.. autoclass:: Role()
    :members:

RoleTags
~~~~~~~~

.. attributetable:: RoleTags

.. autoclass:: RoleTags()
    :members:

Events
------

- :func:`on_guild_role_create(role) <disnake.on_guild_role_create>`
- :func:`on_guild_role_delete(role) <disnake.on_guild_role_delete>`
- :func:`on_guild_role_update(before, after) <disnake.on_guild_role_update>`
