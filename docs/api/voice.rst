.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Voice
=====

This section documents everything related to voice connections.

Classes
-------

VoiceClient
~~~~~~~~~~~

.. attributetable:: VoiceClient

.. autoclass:: VoiceClient()
    :members:
    :exclude-members: connect, on_voice_state_update, on_voice_server_update

VoiceProtocol
~~~~~~~~~~~~~

.. attributetable:: VoiceProtocol

.. autoclass:: VoiceProtocol
    :members:

AudioSource
~~~~~~~~~~~

.. attributetable:: AudioSource

.. autoclass:: AudioSource
    :members:

PCMAudio
~~~~~~~~

.. attributetable:: PCMAudio

.. autoclass:: PCMAudio
    :members:

FFmpegAudio
~~~~~~~~~~~

.. attributetable:: FFmpegAudio

.. autoclass:: FFmpegAudio
    :members:

FFmpegPCMAudio
~~~~~~~~~~~~~~

.. attributetable:: FFmpegPCMAudio

.. autoclass:: FFmpegPCMAudio
    :members:

FFmpegOpusAudio
~~~~~~~~~~~~~~~

.. attributetable:: FFmpegOpusAudio

.. autoclass:: FFmpegOpusAudio
    :members:

PCMVolumeTransformer
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: PCMVolumeTransformer

.. autoclass:: PCMVolumeTransformer
    :members:

Opus Library
~~~~~~~~~~~~

.. autofunction:: disnake.opus.load_opus

.. autofunction:: disnake.opus.is_loaded

Discord Models
---------------

VoiceState
~~~~~~~~~~

.. attributetable:: VoiceState

.. autoclass:: VoiceState()
    :members:

VoiceRegion
~~~~~~~~~~~

.. attributetable:: VoiceRegion

.. autoclass:: VoiceRegion()
    :members:


Enumerations
------------

PartyType
~~~~~~~~~

.. class:: PartyType

    Represents the type of a voice channel activity/application.

    .. attribute:: poker

        The "Poker Night" activity.
    .. attribute:: betrayal

        The "Betrayal.io" activity.
    .. attribute:: fishing

        The "Fishington.io" activity.
    .. attribute:: chess

        The "Chess In The Park" activity.
    .. attribute:: letter_tile

        The "Letter Tile" activity.
    .. attribute:: word_snack

        The "Word Snacks" activity.
    .. attribute:: doodle_crew

        The "Doodle Crew" activity.
    .. attribute:: checkers

        The "Checkers In The Park" activity.

        .. versionadded:: 2.3
    .. attribute:: spellcast

        The "SpellCast" activity.

        .. versionadded:: 2.3
    .. attribute:: watch_together

        The "Watch Together" activity, a Youtube application.

        .. versionadded:: 2.3
    .. attribute:: sketch_heads

        The "Sketch Heads" activity.

        .. versionadded:: 2.4
    .. attribute:: ocho

        The "Ocho" activity.

        .. versionadded:: 2.4
    .. attribute:: gartic_phone

        The "Gartic Phone" activity.

        .. versionadded:: 2.9

Events
------

- :func:`on_voice_state_update(member, before, after) <disnake.on_voice_state_update>`
