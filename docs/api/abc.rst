.. currentmodule:: disnake.abc

.. _discord_abcs_ref:

Abstract Base Classes
=====================

This section documents everything under ``disnake.abc.*``.

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
