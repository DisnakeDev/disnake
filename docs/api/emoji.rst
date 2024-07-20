.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Emojis
======

This section documents everything related to Discord
:ddocs:`emoji <resources/emoji>`.

Discord Models
--------------

Emoji
~~~~~

.. autoclass:: Emoji
    :members:
    :inherited-members:

BaseEmoji
~~~~~~~~~

.. attributetable:: BaseEmoji

.. autoclass:: BaseEmoji
    :members:
    :inherited-members:

GuildEmoji
~~~~~~~~~~

.. attributetable:: GuildEmoji

.. autoclass:: GuildEmoji
    :members:
    :inherited-members:

ApplicationEmoji
~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationEmoji

.. autoclass:: ApplicationEmoji
    :members:
    :inherited-members:

Data Classes
------------

PartialEmoji
~~~~~~~~~~~~

.. attributetable:: PartialEmoji

.. autoclass:: PartialEmoji
    :members:
    :inherited-members:

Events
------

- :func:`on_guild_emojis_update(guild, before, after) <disnake.on_guild_emojis_update>`