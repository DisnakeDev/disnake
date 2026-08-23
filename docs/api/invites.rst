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

GuildInviteFlags
~~~~~~~~~~~~~~~~

.. attributetable:: GuildInviteFlags

.. autoclass:: GuildInviteFlags()
    :members:

Data Classes
------------

TargetUserJob
~~~~~~~~~~~~~

.. class:: TargetUserJob

    A :class:`~typing.NamedTuple` which represents an invite user job from :meth:`Invite.fetch_target_users_job_status`.

    .. attribute:: status

        The status of the job: :data:`0 (UNSPECIFIED)` is the default value; :data:`1 (PROCESSING)` means the job is currently being processed; :data:`2 (COMPLETED)` means the job has been completed successfully; :data:`3 (FAILED)` means the job has failed, see ``error_message`` attribute for more details

        :type: :class:`int`
    .. attribute:: total_users

        The total number of targeted users

        :type: :class:`int`
    .. attribute:: processed_users

        The total number of processed users so far
        
        :type: :class:`int`
    .. attribute:: created_at

        The date when the job started
        
        :type: :class:`~datetime.datetime`
    .. attribute:: completed_at

        The date when the job was completed, :data:`None` if it's still running
        
        :type: :class:`~datetime.datetime` | :data:`None`
    .. attribute:: error_message

        The error message of the job, if any

        :type: :class:`str` | :data:`None`

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
