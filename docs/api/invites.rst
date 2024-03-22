.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Invites
=======

This section documents everything related to invites.

Discord Models
---------------

Invite
~~~~~~

.. attributetable:: Invite

.. autoclass:: Invite()
    :members:

PartialInviteGuild
~~~~~~~~~~~~~~~~~~

.. attributetable:: PartialInviteGuild

.. autoclass:: PartialInviteGuild()
    :members:

PartialInviteChannel
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: PartialInviteChannel

.. autoclass:: PartialInviteChannel()
    :members:

Enumerations
------------

InviteType
~~~~~~~~~~

.. class:: InviteType

    Represents the type of an invite.

    .. versionadded:: 2.10

    .. attribute:: guild

        Represents an invite to a guild.

    .. attribute:: group_dm

        Represents an invite to a group channel.

    .. attribute:: friend

        Represents a friend invite.

InviteTarget
~~~~~~~~~~~~

.. class:: InviteTarget

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

- :func:`on_invite_create(invite) <disnake.on_invite_create>`
- :func:`on_invite_delete(invite) <disnake.on_invite_delete>`
