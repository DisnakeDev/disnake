.. currentmodule:: disnake

Invites
=======

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

Check out the :ref:`related events <related_events_invite>`!
