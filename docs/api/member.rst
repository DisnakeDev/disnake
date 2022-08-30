.. currentmodule:: disnake

Member
======

This sections documents everything related to guild members.

Classes
-------

Member
~~~~~~

.. attributetable:: Member

.. autoclass:: Member()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

VoiceState
~~~~~~~~~~~

.. attributetable:: VoiceState

.. autoclass:: VoiceState()
    :members:

Events
------

.. function:: on_member_join(member)
              on_member_remove(member)

    |discord_events|

    Called when a :class:`Member` leaves or joins a :class:`Guild`.

    This requires :attr:`Intents.members` to be enabled.

    :param member: The member who joined or left.
    :type member: :class:`Member`

.. function:: on_member_update(before, after)

    |discord_event|

    Called when a :class:`Member` is updated.

    This is called when one or more of the following things change, but is not limited to:

    - avatar (guild-specific)
    - current_timeout
    - nickname
    - pending
    - premium_since
    - roles

    This requires :attr:`Intents.members` to be enabled.

    :param before: The member's old info.
    :type before: :class:`Member`
    :param after: The member's updated info.
    :type after: :class:`Member`

.. function:: on_member_ban(guild, user)

    |discord_event|

    Called when user gets banned from a :class:`Guild`.

    This requires :attr:`Intents.bans` to be enabled.

    :param guild: The guild the user got banned from.
    :type guild: :class:`Guild`
    :param user: The user that got banned.
                 Can be either :class:`User` or :class:`Member` depending on
                 whether the user was in the guild at the time of removal.
    :type user: Union[:class:`User`, :class:`Member`]

.. function:: on_member_unban(guild, user)

    |discord_event|

    Called when a :class:`User` gets unbanned from a :class:`Guild`.

    This requires :attr:`Intents.bans` to be enabled.

    :param guild: The guild the user got unbanned from.
    :type guild: :class:`Guild`
    :param user: The user that got unbanned.
    :type user: :class:`User`
