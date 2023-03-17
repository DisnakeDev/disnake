.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Stage Instances
===============

This section documents everything related to :ddocs:`stage instances <resources/stage-instance>`,
which contain information about currently live stages.

Discord Models
---------------

StageInstance
~~~~~~~~~~~~~

.. attributetable:: StageInstance

.. autoclass:: StageInstance()
    :members:

Enumerations
------------

StagePrivacyLevel
~~~~~~~~~~~~~~~~~

.. class:: StagePrivacyLevel

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

- :func:`on_stage_instance_create(stage_instance) <disnake.on_stage_instance_create>`
- :func:`on_stage_instance_delete(stage_instance) <disnake.on_stage_instance_delete>`
- :func:`on_stage_instance_update(before, after) <disnake.on_stage_instance_update>`
