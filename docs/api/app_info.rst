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

Data Classes
------------

ApplicationFlags
~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationFlags

.. autoclass:: ApplicationFlags
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
