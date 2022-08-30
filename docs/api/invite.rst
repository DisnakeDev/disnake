.. currentmodule:: disnake

Invite
======

This section documents everything related to channel invites.

Classes
-------

Invite
~~~~~~~

.. attributetable:: Invite

.. autoclass:: Invite()
    :members:

Data Classes
------------

PartialInviteGuild
~~~~~~~~~~~~~~~~~~~

.. attributetable:: PartialInviteGuild

.. autoclass:: PartialInviteGuild()
    :members:

PartialInviteChannel
~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: PartialInviteChannel

.. autoclass:: PartialInviteChannel()
    :members:

Enumerations
------------

InviteTarget
~~~~~~~~~~~~

.. class:: InviteTarget

    |discord_enum|

    Represents the invite type for voice channel invites.

    .. versionadded:: 2.0

    .. attribute:: unknown

        The invite doesn't target anyone or anything.

    .. attribute:: stream

        A stream invite that targets a user.

    .. attribute:: embedded_application

        A stream invite that targets an embedded application.

Events
------

.. function:: on_invite_create(invite)
              on_invite_delete(invite)

    |discord_events|

    Called when an :class:`Invite` is created/deleted.
    You must have the :attr:`~Permissions.manage_channels` permission to receive this.

    .. versionadded:: 1.3

    .. note::

        There is a rare possibility that the :attr:`Invite.guild` and :attr:`Invite.channel`
        attributes will be of :class:`Object` rather than the respective models.

    This requires :attr:`Intents.invites` to be enabled.

    :param invite: The invite that was created/deleted.
    :type invite: :class:`Invite`
