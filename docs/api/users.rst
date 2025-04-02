.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Users
=====

This section documents everything related to users.

Discord Models
--------------

User
~~~~

.. attributetable:: User

.. autoclass:: User()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

Data Classes
------------

PublicUserFlags
~~~~~~~~~~~~~~~

.. attributetable:: PublicUserFlags

.. autoclass:: PublicUserFlags()
    :members:

MemberFlags
~~~~~~~~~~~

.. attributetable:: MemberFlags

.. autoclass:: MemberFlags()
    :members:

Enumerations
------------

UserFlags
~~~~~~~~~

.. autoclass:: UserFlags()
    :members:

DefaultAvatar
~~~~~~~~~~~~~

.. autoclass:: DefaultAvatar()
    :members:

Events
------

- :func:`on_user_update(before, after) <disnake.on_user_update>`
