.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Emojis
======

This section documents everything related to Discord
:ddocs:`emoji <resources/emoji>`.

Discord Models
---------------

Emoji
~~~~~

.. autoclass:: Emoji
   :members:
   :inherited-members:

BaseEmoji
~~~~~~~~~

.. autoclass:: disnake.BaseEmoji
   :members:
   :inherited-members:

.. attributetable:: BaseEmoji

GuildEmoji
~~~~~~~~~~

.. autoclass:: disnake.GuildEmoji
   :members:
   :inherited-members:

.. attributetable:: GuildEmoji

ApplicationEmoji
~~~~~~~~~~~~~~~~~

.. autoclass:: disnake.ApplicationEmoji
   :members:
   :inherited-members:

.. attributetable:: ApplicationEmoji

Data Classes
------------

PartialEmoji
~~~~~~~~~~~~

.. autoclass:: disnake.PartialEmoji
   :members:
   :inherited-members:

.. attributetable:: PartialEmoji

Events
------

- :func:`on_guild_emojis_update(guild, before, after) <disnake.on_guild_emojis_update>`
