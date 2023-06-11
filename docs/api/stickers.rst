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

.. class:: StickerType

    Represents the type of sticker.

    .. versionadded:: 2.0

    .. attribute:: standard

        Represents a standard sticker that all Nitro users can use.

    .. attribute:: guild

        Represents a custom sticker created in a guild.

StickerFormatType
~~~~~~~~~~~~~~~~~

.. class:: StickerFormatType

    Represents the type of sticker images.

    .. versionadded:: 1.6

    .. attribute:: png

        Represents a sticker with a png image.

    .. attribute:: apng

        Represents a sticker with an apng image.

    .. attribute:: lottie

        Represents a sticker with a lottie image.

    .. attribute:: gif

        Represents a sticker with a gif image.

        .. versionadded:: 2.8

Events
------

- :func:`on_guild_stickers_update(guild, before, after) <disnake.on_guild_stickers_update>`
