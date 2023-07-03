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

.. autoclass:: PartialSoundboardSound
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

RawSoundboardSoundDeleteEvent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawSoundboardSoundDeleteEvent

.. autoclass:: RawSoundboardSoundDeleteEvent()
    :members:


Events
------

- :func:`on_soundboard_sound_create(sound) <disnake.on_soundboard_sound_create>`
- :func:`on_raw_soundboard_sound_update(sound) <disnake.on_raw_soundboard_sound_update>`
- :func:`on_raw_soundboard_sound_delete(sound) <disnake.on_raw_soundboard_sound_delete>`
