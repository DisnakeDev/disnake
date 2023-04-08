.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Clients
=======

This section documents everything related to :class:`Client` and it's connectivity to Discord.

If this is your first time working with disnake, it is highly recommended to read
:ref:`Getting Started <getting_started>` articles first.

Classes
-------

Client
~~~~~~

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

Discord Models
---------------

ClientUser
~~~~~~~~~~

.. attributetable:: ClientUser

.. autoclass:: ClientUser()
    :members:
    :inherited-members:

SessionStartLimit
~~~~~~~~~~~~~~~~~

.. attributetable:: SessionStartLimit

.. autoclass:: SessionStartLimit()
    :members:

Data Classes
------------

ShardInfo
~~~~~~~~~

.. attributetable:: ShardInfo

.. autoclass:: ShardInfo()
    :members:

GatewayParams
~~~~~~~~~~~~~

.. attributetable:: GatewayParams

.. autoclass:: GatewayParams()
    :members:
    :exclude-members: encoding, zlib

Intents
~~~~~~~

.. attributetable:: Intents

.. autoclass:: Intents
    :members:

MemberCacheFlags
~~~~~~~~~~~~~~~~

.. attributetable:: MemberCacheFlags

.. autoclass:: MemberCacheFlags
    :members:


Events
------

- :func:`on_connect() <disnake.on_connect>`
- :func:`on_disconnect() <disnake.on_disconnect>`
- :func:`on_error(event, *args, **kwargs) <disnake.on_error>`
- :func:`on_gateway_error(event, data, shard_id, exc) <disnake.on_gateway_error>`
- :func:`on_ready() <disnake.on_ready>`
- :func:`on_resumed() <disnake.on_resumed>`
- :func:`on_shard_connect(shard_id) <disnake.on_shard_connect>`
- :func:`on_shard_disconnect(shard_id) <disnake.on_shard_disconnect>`
- :func:`on_shard_ready(shard_id) <disnake.on_shard_ready>`
- :func:`on_shard_resumed(shard_id) <disnake.on_shard_resumed>`
- :func:`on_socket_event_type(event_type) <disnake.on_socket_event_type>`
- :func:`on_socket_raw_receive(msg) <disnake.on_socket_raw_receive>`
- :func:`on_socket_raw_send(payload) <disnake.on_socket_raw_send>`
