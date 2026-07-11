.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Soundboard
==========

This section documents everything related to Discord
:ddocs:`soundboards <resources/soundboard>`.

Discord Models
--------------

PartialSoundboardSound
~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: PartialSoundboardSound

.. autoclass:: PartialSoundboardSound()
    :members:
    :inherited-members:

SoundboardSound
~~~~~~~~~~~~~~~

.. attributetable:: SoundboardSound

.. autoclass:: SoundboardSound()
    :members:
    :inherited-members:

GuildSoundboardSound
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: GuildSoundboardSound

.. autoclass:: GuildSoundboardSound()
    :members:
    :inherited-members:


Events
------

- :func:`on_guild_soundboard_sounds_update(guild, before, after) <disnake.on_guild_soundboard_sounds_update>`
