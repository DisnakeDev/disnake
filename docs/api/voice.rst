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

VoiceChannelEffect
~~~~~~~~~~~~~~~~~~

.. attributetable:: VoiceChannelEffect

.. autoclass:: VoiceChannelEffect()
    :members:

RawVoiceChannelEffectEvent
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: RawVoiceChannelEffectEvent

.. autoclass:: RawVoiceChannelEffectEvent()
    :members:


Enumerations
------------

VoiceChannelEffectAnimationType
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: VoiceChannelEffectAnimationType()
    :members:

PartyType
~~~~~~~~~

.. autoclass:: PartyType()
    :members:

Events
------

- :func:`on_voice_state_update(member, before, after) <disnake.on_voice_state_update>`
- :func:`on_voice_channel_effect(channel, member, effect) <disnake.on_voice_channel_effect>`
- :func:`on_raw_voice_channel_effect(payload) <disnake.on_raw_voice_channel_effect>`
