.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake.ext.commands

.. _ext_commands_api_checks:

Checks
======

This section documents checks - special decorators intented to simplify working with Discord-specific conditions.

Classes
-------

Cooldown
~~~~~~~~

.. attributetable:: Cooldown

.. autoclass:: Cooldown
    :members:

Enumerations
------------

BucketType
~~~~~~~~~~

.. class:: BucketType

    Specifies a type of bucket for, e.g. a cooldown.

    .. attribute:: default

        The default bucket operates on a global basis.
    .. attribute:: user

        The user bucket operates on a per-user basis.
    .. attribute:: guild

        The guild bucket operates on a per-guild basis.
    .. attribute:: channel

        The channel bucket operates on a per-channel basis.
    .. attribute:: member

        The member bucket operates on a per-member basis.
    .. attribute:: category

        The category bucket operates on a per-category basis.
    .. attribute:: role

        The role bucket operates on a per-role basis.

        .. versionadded:: 1.3

Functions
---------

.. autofunction:: check(predicate)
    :decorator:

.. autofunction:: check_any(*checks)
    :decorator:

.. autofunction:: has_role(item)
    :decorator:

.. autofunction:: has_permissions(**perms)
    :decorator:

.. autofunction:: has_guild_permissions(**perms)
    :decorator:

.. autofunction:: has_any_role(*items)
    :decorator:

.. autofunction:: bot_has_role(item)
    :decorator:

.. autofunction:: bot_has_permissions(**perms)
    :decorator:

.. autofunction:: bot_has_guild_permissions(**perms)
    :decorator:

.. autofunction:: bot_has_any_role(*items)
    :decorator:

.. autofunction:: cooldown(rate, per, type=BucketType.default)
    :decorator:

.. autofunction:: dynamic_cooldown(cooldown, type=BucketType.default)
    :decorator:

.. autofunction:: max_concurrency(number, per=BucketType.default, *, wait=False)
    :decorator:

.. autofunction:: before_invoke(coro)
    :decorator:

.. autofunction:: after_invoke(coro)
    :decorator:

.. autofunction:: guild_only(,)
    :decorator:

.. autofunction:: dm_only(,)
    :decorator:

.. autofunction:: is_owner(,)
    :decorator:

.. autofunction:: is_nsfw(,)
    :decorator:

.. autofunction:: default_member_permissions(value=0, **permissions)
    :decorator:
