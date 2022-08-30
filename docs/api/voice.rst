.. currentmodule:: disnake

Voice Related
=============

This section documents everything related to interaction with Discord voice.

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

Enumerations
------------

PartyType
~~~~~~~~~

.. class:: PartyType

    |discord_enum|

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

Events
------

.. function:: on_voice_state_update(member, before, after)

    |discord_event|

    Called when a :class:`Member` changes their :class:`VoiceState`.

    The following, but not limited to, examples illustrate when this event is called:

    - A member joins a voice or stage channel.
    - A member leaves a voice or stage channel.
    - A member is muted or deafened by their own accord.
    - A member is muted or deafened by a guild administrator.

    This requires :attr:`Intents.voice_states` to be enabled.

    :param member: The member whose voice states changed.
    :type member: :class:`Member`
    :param before: The voice state prior to the changes.
    :type before: :class:`VoiceState`
    :param after: The voice state after the changes.
    :type after: :class:`VoiceState`
