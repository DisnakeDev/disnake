.. currentmodule:: disnake

Channels
========

This section documents everything related to channels and threads.

Classes
-------

TextChannel
~~~~~~~~~~~

.. attributetable:: TextChannel

.. autoclass:: TextChannel()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

VoiceChannel
~~~~~~~~~~~~

.. attributetable:: VoiceChannel

.. autoclass:: VoiceChannel()
    :members:
    :inherited-members:

CategoryChannel
~~~~~~~~~~~~~~~~~

.. attributetable:: CategoryChannel

.. autoclass:: CategoryChannel()
    :members:
    :inherited-members:

Thread
~~~~~~

.. attributetable:: Thread

.. autoclass:: Thread()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

ThreadMember
~~~~~~~~~~~~

.. attributetable:: ThreadMember

.. autoclass:: ThreadMember()
    :members:

StageChannel
~~~~~~~~~~~~

.. attributetable:: StageChannel

.. autoclass:: StageChannel()
    :members:
    :inherited-members:

ForumChannel
~~~~~~~~~~~~

.. attributetable:: ForumChannel

.. autoclass:: ForumChannel()
    :members:
    :inherited-members:
    :exclude-members: typing

    .. automethod:: typing
        :async-with:

DMChannel
~~~~~~~~~

.. attributetable:: DMChannel

.. autoclass:: DMChannel()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

GroupChannel
~~~~~~~~~~~~

.. attributetable:: GroupChannel

.. autoclass:: GroupChannel()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

PartialMessageable
~~~~~~~~~~~~~~~~~~

.. attributetable:: PartialMessageable

.. autoclass:: PartialMessageable()
    :members:
    :inherited-members:

Data Classes
------------

ChannelFlags
~~~~~~~~~~~~

.. attributetable:: ChannelFlags

.. autoclass:: ChannelFlags
    :members:

VoiceRegion
~~~~~~~~~~~

.. attributetable:: VoiceRegion

.. autoclass:: VoiceRegion()
    :members:

RawThreadDeleteEvent
~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawThreadDeleteEvent

.. autoclass:: RawThreadDeleteEvent()
    :members:

RawThreadMemberRemoveEvent
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawThreadMemberRemoveEvent

.. autoclass:: RawThreadMemberRemoveEvent()
    :members:

Enumerations
------------

ChannelType
~~~~~~~~~~~

.. class:: ChannelType

    |discord_enum|

    Specifies the type of channel.

    .. attribute:: text

        A text channel.
    .. attribute:: voice

        A voice channel.
    .. attribute:: private

        A private text channel. Also called a direct message.
    .. attribute:: group

        A private group text channel.
    .. attribute:: category

        A category channel.
    .. attribute:: news

        A guild news channel.

    .. attribute:: stage_voice

        A guild stage voice channel.

        .. versionadded:: 1.7

    .. attribute:: news_thread

        A news thread.

        .. versionadded:: 2.0

    .. attribute:: public_thread

        A public thread.

        .. versionadded:: 2.0

    .. attribute:: private_thread

        A private thread.

        .. versionadded:: 2.0

    .. attribute:: guild_directory

        A student hub channel.

        .. versionadded:: 2.1

    .. attribute:: forum

        A channel of only threads.

        .. versionadded:: 2.5

ThreadArchiveDuration
~~~~~~~~~~~~~~~~~~~~~

.. class:: ThreadArchiveDuration

    |discord_enum|

    Represents the automatic archive duration of a thread in minutes.

    .. versionadded:: 2.3

    .. attribute:: hour

        The thread will archive after an hour of inactivity.

    .. attribute:: day

        The thread will archive after a day of inactivity.

    .. attribute:: three_days

        The thread will archive after three days of inactivity.

    .. attribute:: week

        The thread will archive after a week of inactivity.

VideoQualityMode
~~~~~~~~~~~~~~~~

.. class:: VideoQualityMode

    |discord_enum|

    Represents the camera video quality mode for voice channel participants.

    .. versionadded:: 2.0

    .. attribute:: auto

        Represents auto camera video quality.

    .. attribute:: full

        Represents full camera video quality.
