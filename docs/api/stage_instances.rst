.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Stage Instances
===============

This section documents everything related to stage instances - TODO: understand what stage instances are

Classes
-------

StageInstance
~~~~~~~~~~~~~~

.. attributetable:: StageInstance

.. autoclass:: StageInstance()
    :members:

Enumerations
------------

StagePrivacyLevel
~~~~~~~~~~~~~~~~~

.. class:: StagePrivacyLevel

    |discord_enum|

    Represents a stage instance's privacy level.

    .. versionadded:: 2.0

    .. attribute:: public

        The stage instance can be joined by external users.

        .. deprecated:: 2.5

            Public stages are no longer supported by discord.

    .. attribute:: closed

        The stage instance can only be joined by members of the guild.

    .. attribute:: guild_only

        Alias for :attr:`.closed`

Events
------

- :func:`disnake.on_stage_instance_create(stage_instance)`
- :func:`disnake.on_stage_instance_delete(stage_instance)`
- :func:`disnake.on_stage_instance_update(before, after)`

See all :ref:`related events <related_events_stage_instance>`!
