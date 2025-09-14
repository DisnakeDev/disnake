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

.. autoclass:: StagePrivacyLevel()
    :members:

Events
------

- :func:`on_stage_instance_create(stage_instance) <disnake.on_stage_instance_create>`
- :func:`on_stage_instance_delete(stage_instance) <disnake.on_stage_instance_delete>`
- :func:`on_stage_instance_update(before, after) <disnake.on_stage_instance_update>`
