.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Activities
==========

This section documents everything related to :class:`User`'s and :class:`Member`'s activities.

Discord Models
--------------

Spotify
~~~~~~~

.. attributetable:: Spotify

.. autoclass:: Spotify()
    :members:
    :inherited-members:

Data Classes
------------

BaseActivity
~~~~~~~~~~~~

.. attributetable:: BaseActivity

.. autoclass:: BaseActivity
    :members:
    :inherited-members:

Activity
~~~~~~~~

.. attributetable:: Activity

.. autoclass:: Activity
    :members:
    :inherited-members:

Game
~~~~

.. attributetable:: Game

.. autoclass:: Game
    :members:
    :inherited-members:

Streaming
~~~~~~~~~

.. attributetable:: Streaming

.. autoclass:: Streaming
    :members:
    :inherited-members:

CustomActivity
~~~~~~~~~~~~~~

.. attributetable:: CustomActivity

.. autoclass:: CustomActivity
    :members:
    :inherited-members:

Enumerations
------------

ActivityType
~~~~~~~~~~~~

.. class:: ActivityType

    Specifies the type of :class:`Activity`. This is used to check how to
    interpret the activity itself.

    .. attribute:: unknown

        An unknown activity type. This should generally not happen.
    .. attribute:: playing

        A "Playing" activity type.
    .. attribute:: streaming

        A "Streaming" activity type.
    .. attribute:: listening

        A "Listening" activity type.
    .. attribute:: watching

        A "Watching" activity type.
    .. attribute:: custom

        A custom activity type.
    .. attribute:: competing

        A competing activity type.

        .. versionadded:: 1.5

Status
~~~~~~

.. class:: Status

    Specifies a :class:`Member` 's status.

    .. attribute:: online

        The member is online.
    .. attribute:: offline

        The member is offline.
    .. attribute:: idle

        The member is idle.
    .. attribute:: dnd

        The member is "Do Not Disturb".
    .. attribute:: do_not_disturb

        An alias for :attr:`dnd`.
    .. attribute:: invisible

        The member is "invisible". In reality, this is only used in sending
        a presence a la :meth:`Client.change_presence`. When you receive a
        user's presence this will be :attr:`offline` instead.
    .. attribute:: streaming

        The member is live streaming to Twitch or YouTube.

        .. versionadded:: 2.3

Events
------

- :func:`on_presence_update(before, after) <disnake.on_presence_update>`
