.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Application Info
================

This section documents everything related to application information.

Discord Models
--------------

AppInfo
~~~~~~~

.. attributetable:: AppInfo

.. autoclass:: AppInfo()
    :members:

PartialAppInfo
~~~~~~~~~~~~~~

.. attributetable:: PartialAppInfo

.. autoclass:: PartialAppInfo()
    :members:

InstallParams
~~~~~~~~~~~~~

.. attributetable:: InstallParams

.. autoclass:: InstallParams()
    :members:

Team
~~~~

.. attributetable:: Team

.. autoclass:: Team()
    :members:

TeamMember
~~~~~~~~~~

.. attributetable:: TeamMember

.. autoclass:: TeamMember()
    :members:
    :inherited-members:

Data Classes
------------

ApplicationFlags
~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationFlags

.. autoclass:: ApplicationFlags
    :members:

ApplicationRoleConnectionMetadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationRoleConnectionMetadata

.. autoclass:: ApplicationRoleConnectionMetadata
    :members:

Enumerations
------------

TeamMembershipState
~~~~~~~~~~~~~~~~~~~

.. class:: TeamMembershipState

    Represents the membership state of a team member retrieved through :func:`Client.application_info`.

    .. versionadded:: 1.3

    .. attribute:: invited

        Represents an invited member.

    .. attribute:: accepted

        Represents a member currently in the team.

TeamMemberRole
~~~~~~~~~~~~~~

.. class:: TeamMemberRole

    Represents the role of a team member retrieved through :func:`Client.application_info`.

    .. versionadded:: 2.10

    .. attribute:: admin

        Admins have the most permissions. An admin can only take destructive actions on the team or team-owned apps if they are the team owner.

    .. attribute:: developer

        Developers can access information about a team and team-owned applications, and take limited actions on them, like configuring interaction endpoints or resetting the bot token.

    .. attribute:: read_only

        Read-only members can access information about a team and team-owned applications.

ApplicationRoleConnectionMetadataType
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: ApplicationRoleConnectionMetadataType

    Represents the type of a role connection metadata value.

    These offer comparison operations, which allow guilds to configure role requirements
    based on the metadata value for each user and a guild-specified configured value.

    .. versionadded:: 2.8

    .. attribute:: integer_less_than_or_equal

        The metadata value (``integer``) is less than or equal to the guild's configured value.

    .. attribute:: integer_greater_than_or_equal

        The metadata value (``integer``) is greater than or equal to the guild's configured value.

    .. attribute:: integer_equal

        The metadata value (``integer``) is equal to the guild's configured value.

    .. attribute:: integer_not_equal

        The metadata value (``integer``) is not equal to the guild's configured value.

    .. attribute:: datetime_less_than_or_equal

        The metadata value (``ISO8601 string``) is less than or equal to the guild's configured value (``integer``; days before current date).

    .. attribute:: datetime_greater_than_or_equal

        The metadata value (``ISO8601 string``) is greater than or equal to the guild's configured value (``integer``; days before current date).

    .. attribute:: boolean_equal

        The metadata value (``integer``) is equal to the guild's configured value.

    .. attribute:: boolean_not_equal

        The metadata value (``integer``) is not equal to the guild's configured value.
