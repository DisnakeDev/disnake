.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake.abc

.. _disnake_api_abc:

Abstract Base Classes
=====================

This section documents everything under ``disnake.abc.*``.

Abstract Base Classes (commonly referred to as ABC) are classes that other classes can inherit to
get or override specific behaviour. Read more about them :ref:`here <disnake_abc>`.

Classes
-------

Snowflake
~~~~~~~~~

.. attributetable:: Snowflake

.. autoclass:: Snowflake()
    :members:

User
~~~~

.. attributetable:: User

.. autoclass:: User()
    :members:

PrivateChannel
~~~~~~~~~~~~~~

.. attributetable:: PrivateChannel

.. autoclass:: PrivateChannel()
    :members:

GuildChannel
~~~~~~~~~~~~

.. attributetable:: GuildChannel

.. autoclass:: GuildChannel()
    :members:

Messageable
~~~~~~~~~~~

.. attributetable:: Messageable

.. autoclass:: Messageable()
    :members:
    :exclude-members: history, typing

    .. automethod:: Messageable.history
        :async-for:

    .. automethod:: Messageable.typing
        :async-with:

Connectable
~~~~~~~~~~~

.. attributetable:: Connectable

.. autoclass:: Connectable()
