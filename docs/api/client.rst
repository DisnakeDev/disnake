.. currentmodule:: disnake

Clients
=======

This section documents everything related to :class:`Client` and it's connectivity to Discord.

Classes
-------

Client
~~~~~~~

.. attributetable:: Client

.. autoclass:: Client
    :members:
    :exclude-members: fetch_guilds, event

    .. automethod:: Client.event()
        :decorator:

    .. automethod:: Client.fetch_guilds
        :async-for:

AutoShardedClient
~~~~~~~~~~~~~~~~~

.. attributetable:: AutoShardedClient

.. autoclass:: AutoShardedClient
    :members:

ClientUser
~~~~~~~~~~~~

.. attributetable:: ClientUser

.. autoclass:: ClientUser()
    :members:
    :inherited-members:

Data classes
------------

ShardInfo
~~~~~~~~~

.. attributetable:: ShardInfo

.. autoclass:: ShardInfo()
    :members:

SessionStartLimit
~~~~~~~~~~~~~~~~~

.. attributetable:: SessionStartLimit

.. autoclass:: SessionStartLimit()
    :members:

GatewayParams
~~~~~~~~~~~~~~

.. attributetable:: GatewayParams

.. autoclass:: GatewayParams()
    :members:
    :exclude-members: encoding, zlib

Intents
~~~~~~~~~~

.. attributetable:: Intents

.. autoclass:: Intents
    :members:

MemberCacheFlags
~~~~~~~~~~~~~~~~~~

.. attributetable:: MemberCacheFlags

.. autoclass:: MemberCacheFlags
    :members:


Events
------

Check out the :ref:`related events <related_events_client>`!
