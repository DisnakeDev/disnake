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

Check out the :ref:`related events <related_events_member>`!
