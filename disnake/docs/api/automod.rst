.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

AutoMod
=======

This section documents everything related to Discord's :ddocs:`AutoMod features <resources/auto-moderation>`.

Discord Models
---------------

AutoModRule
~~~~~~~~~~~

.. attributetable:: AutoModRule

.. autoclass:: AutoModRule()
    :members:

AutoModActionExecution
~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoModActionExecution

.. autoclass:: AutoModActionExecution()
    :members:

Data Classes
------------

AutoModKeywordPresets
~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoModKeywordPresets

.. autoclass:: AutoModKeywordPresets
    :members:

AutoModTriggerMetadata
~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoModTriggerMetadata

.. autoclass:: AutoModTriggerMetadata
    :members:

AutoModAction
~~~~~~~~~~~~~

.. attributetable:: AutoModAction

.. autoclass:: AutoModAction()
    :members:

AutoModBlockMessageAction
~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoModBlockMessageAction

.. autoclass:: AutoModBlockMessageAction
    :members:

AutoModSendAlertAction
~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoModSendAlertAction

.. autoclass:: AutoModSendAlertAction
    :members:

AutoModTimeoutAction
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoModTimeoutAction

.. autoclass:: AutoModTimeoutAction
    :members:

Enumerations
------------

AutoModActionType
~~~~~~~~~~~~~~~~~

.. autoclass:: AutoModActionType()
    :members:

AutoModEventType
~~~~~~~~~~~~~~~~

.. autoclass:: AutoModEventType()
    :members:

AutoModTriggerType
~~~~~~~~~~~~~~~~~~

.. autoclass:: AutoModTriggerType()
    :members:

Events
------

- :func:`on_automod_action_execution(execution) <disnake.on_automod_action_execution>`
- :func:`on_automod_rule_create(rule) <disnake.on_automod_rule_create>`
- :func:`on_automod_rule_update(rule) <disnake.on_automod_rule_update>`
- :func:`on_automod_rule_delete(rule) <disnake.on_automod_rule_delete>`
