.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Guilds
======

This section documents everything related to
:ddocs:`Guilds <resources/guild>` - main hubs for communication in Discord,
referred to as Servers in the official UI.

Discord Models
---------------

Guild
~~~~~

.. attributetable:: Guild

.. autoclass:: Guild()
    :members:
    :exclude-members: fetch_members, audit_logs

    .. automethod:: fetch_members
        :async-for:

    .. automethod:: audit_logs
        :async-for:

GuildPreview
~~~~~~~~~~~~

.. attributetable:: GuildPreview

.. autoclass:: GuildPreview()
    :members:

Template
~~~~~~~~

.. attributetable:: Template

.. autoclass:: Template()
    :members:

WelcomeScreen
~~~~~~~~~~~~~

.. attributetable:: WelcomeScreen

.. autoclass:: WelcomeScreen()
    :members:

BanEntry
~~~~~~~~

.. class:: BanEntry

    A namedtuple which represents a ban returned from :meth:`~Guild.bans`.

    .. attribute:: reason

        The reason this user was banned.

        :type: Optional[:class:`str`]
    .. attribute:: user

        The :class:`User` that was banned.

        :type: :class:`User`

Onboarding
~~~~~~~~~~

.. attributetable:: Onboarding

.. autoclass:: Onboarding()
    :members:

OnboardingPrompt
~~~~~~~~~~~~~~~~

.. attributetable:: OnboardingPrompt

.. autoclass:: OnboardingPrompt()
    :members:

OnboardingPromptOption
~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: OnboardingPromptOption

.. autoclass:: OnboardingPromptOption()
    :members:

Data Classes
------------

SystemChannelFlags
~~~~~~~~~~~~~~~~~~

.. attributetable:: SystemChannelFlags

.. autoclass:: SystemChannelFlags()
    :members:

WelcomeScreenChannel
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: WelcomeScreenChannel

.. autoclass:: WelcomeScreenChannel()

GuildBuilder
~~~~~~~~~~~~~

.. attributetable:: GuildBuilder

.. autoclass:: GuildBuilder()
    :members:
    :exclude-members: add_category_channel

Enumerations
------------

VerificationLevel
~~~~~~~~~~~~~~~~~

.. class:: VerificationLevel

    Specifies a :class:`Guild`\'s verification level, which is the criteria in
    which a member must meet before being able to send messages to the guild.

    .. container:: operations

        .. versionadded:: 2.0

        .. describe:: x == y

            Checks if two verification levels are equal.
        .. describe:: x != y

            Checks if two verification levels are not equal.
        .. describe:: x > y

            Checks if a verification level is higher than another.
        .. describe:: x < y

            Checks if a verification level is lower than another.
        .. describe:: x >= y

            Checks if a verification level is higher or equal to another.
        .. describe:: x <= y

            Checks if a verification level is lower or equal to another.

    .. attribute:: none

        No criteria set.
    .. attribute:: low

        Member must have a verified email on their Discord account.
    .. attribute:: medium

        Member must have a verified email and be registered on Discord for more
        than five minutes.
    .. attribute:: high

        Member must have a verified email, be registered on Discord for more
        than five minutes, and be a member of the guild itself for more than
        ten minutes.
    .. attribute:: highest

        Member must have a verified phone on their Discord account.

NotificationLevel
~~~~~~~~~~~~~~~~~

.. class:: NotificationLevel

    Specifies whether a :class:`Guild` has notifications on for all messages or mentions only by default.

    .. container:: operations

        .. versionadded:: 2.0

        .. describe:: x == y

            Checks if two notification levels are equal.
        .. describe:: x != y

            Checks if two notification levels are not equal.
        .. describe:: x > y

            Checks if a notification level is higher than another.
        .. describe:: x < y

            Checks if a notification level is lower than another.
        .. describe:: x >= y

            Checks if a notification level is higher or equal to another.
        .. describe:: x <= y

            Checks if a notification level is lower or equal to another.

    .. attribute:: all_messages

        Members receive notifications for every message regardless of them being mentioned.
    .. attribute:: only_mentions

        Members receive notifications for messages they are mentioned in.

ContentFilter
~~~~~~~~~~~~~

.. class:: ContentFilter

    Specifies a :class:`Guild`\'s explicit content filter, which is the machine
    learning algorithms that Discord uses to detect if an image contains
    NSFW content.

    .. container:: operations

        .. versionadded:: 2.0

        .. describe:: x == y

            Checks if two content filter levels are equal.
        .. describe:: x != y

            Checks if two content filter levels are not equal.
        .. describe:: x > y

            Checks if a content filter level is higher than another.
        .. describe:: x < y

            Checks if a content filter level is lower than another.
        .. describe:: x >= y

            Checks if a content filter level is higher or equal to another.
        .. describe:: x <= y

            Checks if a content filter level is lower or equal to another.

    .. attribute:: disabled

        The guild does not have the content filter enabled.
    .. attribute:: no_role

        The guild has the content filter enabled for members without a role.
    .. attribute:: all_members

        The guild has the content filter enabled for every member.

NSFWLevel
~~~~~~~~~

.. class:: NSFWLevel

    Represents the NSFW level of a guild.

    .. versionadded:: 2.0

    .. container:: operations

        .. describe:: x == y

            Checks if two NSFW levels are equal.
        .. describe:: x != y

            Checks if two NSFW levels are not equal.
        .. describe:: x > y

            Checks if a NSFW level is higher than another.
        .. describe:: x < y

            Checks if a NSFW level is lower than another.
        .. describe:: x >= y

            Checks if a NSFW level is higher or equal to another.
        .. describe:: x <= y

            Checks if a NSFW level is lower or equal to another.

    .. attribute:: default

        The guild has not been categorised yet.

    .. attribute:: explicit

        The guild contains NSFW content.

    .. attribute:: safe

        The guild does not contain any NSFW content.

    .. attribute:: age_restricted

        The guild may contain NSFW content.


OnboardingPromptType
~~~~~~~~~~~~~~~~~~~~

.. class:: OnboardingPromptType

    Represents the type of onboarding prompt.

    .. versionadded:: 2.9

    .. attribute:: multiple_choice

        The prompt is a multiple choice prompt.

    .. attribute:: dropdown

        The prompt is a dropdown prompt.


Events
------

- :func:`on_guild_join(guild) <disnake.on_guild_join>`
- :func:`on_guild_remove(guild) <disnake.on_guild_remove>`
- :func:`on_guild_update(before, after) <disnake.on_guild_update>`
- :func:`on_guild_available(guild) <disnake.on_guild_available>`
- :func:`on_guild_unavailable(guild) <disnake.on_guild_unavailable>`
