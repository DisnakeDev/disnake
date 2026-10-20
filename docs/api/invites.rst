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

PartialInviteRole
~~~~~~~~~~~~~~~~~

.. attributetable:: PartialInviteRole

.. autoclass:: PartialInviteRole()
    :members:

Data Classes
------------

InviteTargetUsersJob
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: InviteTargetUsersJob

.. autoclass:: InviteTargetUsersJob()


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

InviteTargetUsersJobStatus
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: InviteTargetUsersJobStatus()
    :members:

Events
------

- :func:`on_invite_create(invite) <disnake.on_invite_create>`
- :func:`on_invite_delete(invite) <disnake.on_invite_delete>`
