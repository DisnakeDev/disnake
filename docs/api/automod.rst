.. currentmodule:: disnake

AutoMod
=======

This section documents everything related to guilds' AutoMod feature.

Classes
-------

AutoModRule
~~~~~~~~~~~~

.. attributetable:: AutoModRule

.. autoclass:: AutoModRule()
    :members:

Data Classes
------------

AutoModActionExecution
~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoModActionExecution

.. autoclass:: AutoModActionExecution()
    :members:

AutoModKeywordPresets
~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoModKeywordPresets

.. autoclass:: AutoModKeywordPresets
    :members:

AutoModTriggerMetadata
~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoModTriggerMetadata

.. autoclass:: AutoModTriggerMetadata
    :members:

AutoModAction
~~~~~~~~~~~~~~

.. attributetable:: AutoModAction

.. autoclass:: AutoModAction()
    :members:

AutoModBlockMessageAction
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoModBlockMessageAction

.. autoclass:: AutoModBlockMessageAction
    :members:

AutoModSendAlertAction
~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoModSendAlertAction

.. autoclass:: AutoModSendAlertAction
    :members:

AutoModTimeoutAction
~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AutoModTimeoutAction

.. autoclass:: AutoModTimeoutAction
    :members:

Enumerations
------------

AutoModActionType
~~~~~~~~~~~~~~~~~

.. class:: AutoModActionType

    |discord_enum|

    Represents the type of action an auto moderation rule will take upon execution.

    .. versionadded:: 2.6

    .. attribute:: block_message

        The rule will prevent matching messages from being posted.

    .. attribute:: send_alert_message

        The rule will send an alert to a specified channel.

    .. attribute:: timeout

        The rule will timeout the user that sent the message.

        .. note::
            This action type is only available for rules with trigger type
            :attr:`~AutoModTriggerType.keyword`, and :attr:`~Permissions.moderate_members`
            permissions are required to use it.

AutoModEventType
~~~~~~~~~~~~~~~~

.. class:: AutoModEventType

    |discord_enum|

    Represents the type of event/context an auto moderation rule will be checked in.

    .. versionadded:: 2.6

    .. attribute:: message_send

        The rule will apply when a member sends or edits a message in the guild.

AutoModTriggerType
~~~~~~~~~~~~~~~~~~

.. class:: AutoModTriggerType

    |discord_enum|

    Represents the type of content that can trigger an auto moderation rule.

    .. versionadded:: 2.6

    .. attribute:: keyword

        The rule will filter messages based on a custom keyword list.

        This trigger type requires additional :class:`metadata <AutoModTriggerMetadata>`.

    .. attribute:: harmful_link

        The rule will filter messages containing malicious links.

    .. attribute:: spam

        The rule will filter messages suspected of being spam.

    .. attribute:: keyword_preset

        The rule will filter messages based on predefined lists containing commonly flagged words.

        This trigger type requires additional :class:`metadata <AutoModTriggerMetadata>`.

    .. attribute:: mention_spam

        The rule will filter messages based on the number of member/role mentions they contain.

        This trigger type requires additional :class:`metadata <AutoModTriggerMetadata>`.

Events
------

.. function:: on_automod_action_execution(execution)

    |discord_event|

    Called when an auto moderation action is executed due to a rule triggering for a particular event.
    You must have the :attr:`~Permissions.manage_guild` permission to receive this.

    The guild this action has taken place in can be accessed using :attr:`AutoModActionExecution.guild`.

    This requires :attr:`Intents.automod_execution` to be enabled.

    In addition, :attr:`Intents.message_content` must be enabled to receive non-empty values
    for :attr:`AutoModActionExecution.content` and :attr:`AutoModActionExecution.matched_content`.

    .. note::
        This event will fire once per executed :class:`AutoModAction`, which means it
        will run multiple times when a rule is triggered, if that rule has multiple actions defined.

    .. versionadded:: 2.6

    :param execution: The auto moderation action execution data.
    :type execution: :class:`AutoModActionExecution`

.. function:: on_automod_rule_create(rule)

    |discord_event|

    Called when an :class:`AutoModRule` is created.
    You must have the :attr:`~Permissions.manage_guild` permission to receive this.

    This requires :attr:`Intents.automod_configuration` to be enabled.

    .. versionadded:: 2.6

    :param rule: The auto moderation rule that was created.
    :type rule: :class:`AutoModRule`

.. function:: on_automod_rule_update(rule)

    |discord_event|

    Called when an :class:`AutoModRule` is updated.
    You must have the :attr:`~Permissions.manage_guild` permission to receive this.

    This requires :attr:`Intents.automod_configuration` to be enabled.

    .. versionadded:: 2.6

    :param rule: The auto moderation rule that was updated.
    :type rule: :class:`AutoModRule`

.. function:: on_automod_rule_delete(rule)

    |discord_event|

    Called when an :class:`AutoModRule` is deleted.
    You must have the :attr:`~Permissions.manage_guild` permission to receive this.

    This requires :attr:`Intents.automod_configuration` to be enabled.

    .. versionadded:: 2.6

    :param rule: The auto moderation rule that was deleted.
    :type rule: :class:`AutoModRule`
