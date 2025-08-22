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
    :exclude-members: large_image_url, large_image_text, small_image_url, small_image_text

Enumerations
------------

ActivityType
~~~~~~~~~~~~

.. autoclass:: ActivityType()
    :members:

Status
~~~~~~

.. autoclass:: Status()
    :members:

Events
------

- :func:`on_presence_update(before, after) <disnake.on_presence_update>`
- :func:`on_raw_presence_update(payload) <disnake.on_raw_presence_update>`
