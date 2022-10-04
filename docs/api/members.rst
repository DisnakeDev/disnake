.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Members
=======

This sections documents everything related to guild members.

Classes
-------

Member
~~~~~~

.. attributetable:: Member

.. autoclass:: Member()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

VoiceState
~~~~~~~~~~~

.. attributetable:: VoiceState

.. autoclass:: VoiceState()
    :members:

Data Classes
------------

RawGuildMemberRemoveEvent
~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawGuildMemberRemoveEvent

.. autoclass:: RawGuildMemberRemoveEvent()
    :members:

Events
------

- :func:`disnake.on_member_join(member)`
- :func:`disnake.on_member_remove(member)`
- :func:`disnake.on_member_update(before, after)`
- :func:`disnake.on_raw_member_update(member)`
- :func:`disnake.on_member_ban(guild, user)`
- :func:`disnake.on_member_unban(guild, user)`
- :func:`disnake.on_()`

See all :ref:`related events <related_events_member>`!
