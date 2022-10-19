.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Members
=======

This sections documents everything related to guild members.

Discord Models
---------------

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
~~~~~~~~~~

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

- :func:`on_member_join(member) <disnake.on_member_join>`
- :func:`on_member_remove(member) <disnake.on_member_remove>`
- :func:`on_member_update(before, after) <disnake.on_member_update>`
- :func:`on_raw_member_update(member) <disnake.on_raw_member_update>`
- :func:`on_member_ban(guild, user) <disnake.on_member_ban>`
- :func:`on_member_unban(guild, user) <disnake.on_member_unban>`
- :func:`on_presence_update(before, after) <disnake.on_presence_update>`
- :func:`on_user_update(before, after) <disnake.on_user_update>`

See all :ref:`related events <related_events_member>`!
