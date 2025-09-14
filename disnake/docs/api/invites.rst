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

.. autoclass:: InviteType()
    :members:

InviteTarget
~~~~~~~~~~~~

.. autoclass:: InviteTarget()
    :members:

Events
------

- :func:`on_invite_create(invite) <disnake.on_invite_create>`
- :func:`on_invite_delete(invite) <disnake.on_invite_delete>`
