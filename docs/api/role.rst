.. currentmodule:: disnake

Role
====

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

.. function:: on_guild_role_create(role)
              on_guild_role_delete(role)

    |discord_events|

    Called when a :class:`Guild` creates or deletes a new :class:`Role`.

    To get the guild it belongs to, use :attr:`Role.guild`.

    This requires :attr:`Intents.guilds` to be enabled.

    :param role: The role that was created or deleted.
    :type role: :class:`Role`

.. function:: on_guild_role_update(before, after)

    |discord_event|

    Called when a :class:`Role` is changed guild-wide.

    This requires :attr:`Intents.guilds` to be enabled.

    :param before: The updated role's old info.
    :type before: :class:`Role`
    :param after: The updated role's updated info.
    :type after: :class:`Role`