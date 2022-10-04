.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Clients
=======

This section documents everything related to :class:`Client` and it's connectivity to Discord.

If this is your first time working with disnake, it is highly recommended to read
:ref:`Getting Started <disnake_getting_started>` articles first.

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

- :func:`disnake.on_connect()`
- :func:`disnake.on_disconnect()`
- :func:`disnake.on_error(event, *args, **kwargs)`
- :func:`disnake.on_ready()`
- :func:`disnake.on_resumed()`
- :func:`disnake.on_shard_connect(shard_id)`
- :func:`disnake.on_shard_disconnect(shard_id)`
- :func:`disnake.on_shard_ready(shard_id)`
- :func:`disnake.on_shard_resumed(shard_id)`
- :func:`disnake.on_socket_event_type(event_type)`
- :func:`disnake.on_socket_raw_receive(msg)`
- :func:`disnake.on_socket_raw_send(payload)`
- :func:`disnake.on_gateway_error(event, data, shard_id, exc)`

See all :ref:`related events <related_events_client>`!
