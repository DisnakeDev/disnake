.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Stickers
========

This section documents everything related to stickers.

Discord Models
---------------

Sticker
~~~~~~~

.. attributetable:: Sticker

.. autoclass:: Sticker()
    :members:
    :inherited-members:

StandardSticker
~~~~~~~~~~~~~~~

.. attributetable:: StandardSticker

.. autoclass:: StandardSticker()
    :members:
    :inherited-members:

GuildSticker
~~~~~~~~~~~~

.. attributetable:: GuildSticker

.. autoclass:: GuildSticker()
    :members:
    :inherited-members:

StickerItem
~~~~~~~~~~~

.. attributetable:: StickerItem

.. autoclass:: StickerItem()
    :members:
    :inherited-members:

StickerPack
~~~~~~~~~~~

.. attributetable:: StickerPack

.. autoclass:: StickerPack()
    :members:

Enumerations
------------

StickerType
~~~~~~~~~~~

.. autoclass:: StickerType()
    :members:

StickerFormatType
~~~~~~~~~~~~~~~~~

.. autoclass:: StickerFormatType()
    :members:

Events
------

- :func:`on_guild_stickers_update(guild, before, after) <disnake.on_guild_stickers_update>`
