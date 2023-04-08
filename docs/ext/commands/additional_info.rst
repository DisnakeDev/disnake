.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

.. _ext_commands_additional_info:

Additional info
===============

This section contains explanations of some library mechanics which may be useful to know.

.. _app_command_sync:

App command sync
----------------

If you're using :ref:`disnake_ext_commands` for application commands (slash commands, context menus) you should
understand how your commands show up in Discord. By default, the library registers / updates all commands automatically.
Based on the application commands defined in your code the library automatically determines
which commands should be registered, edited or deleted, but there're some edge cases you should keep in mind.

Unknown Commands
+++++++++++++++++

Unlike global commands, per-guild application commands are synced in a lazy fashion. This is due to Discord ratelimits,
as checking all guilds for application commands is infeasible past two or three guilds.
This can lead to situations where a command no longer exists in the code but still exists in a server.

To rectify this, just run the command. It will automatically be deleted.

.. _changing-test-guilds:

This will also occur when IDs are removed from the ``test_guilds`` kwarg of :class:`Bot <ext.commands.Bot>` (or a similar class) or from the ``guild_ids`` kwarg of
:func:`slash_command <ext.commands.slash_command>`, :func:`user_command <ext.commands.user_command>`, or :func:`message_command <ext.commands.message_command>`.

Command Sync with Multiple Clusters
++++++++++++++++++++++++++++++++++++

If your bot requires shard distribution across several clusters, you should disable command sync on all clusters except one.
This will prevent conflicts and race conditions. Discord API doesn't provide users with events related to application command updates,
so it's impossible to keep the cache of multiple machines synced. Having only 1 cluster with ``sync_commands`` set to ``True`` is enough
because global registration of application commands doesn't depend on sharding.

.. _why_params_and_injections_return_any:

Why do ``Param`` and ``Injection``-related functions return ``Any``?
--------------------------------------------------------------------

If your editor of choice supports type-checking, you may have noticed that :func:`~ext.commands.Param`, :func:`~ext.commands.inject`,
and :func:`~ext.commands.injection` do not have a specific return type, but at runtime these return :class:`~ext.commands.ParamInfo` and
:class:`~ext.commands.Injection` respectively.

A typical example of a slash command might look like this: ::

    @bot.slash_command(description="Replies with the given text!")
    async def echo(
        inter: disnake.ApplicationCommandInteraction,
        text: str = commands.Param(description="Echo~"),
    ) -> None:
        await inter.response.send_message(text)

Here, you have two parameters in your command's function: ``inter``, an instance of :class:`disnake.ApplicationCommandInteraction`, and
``text``, which is somewhat unusual: you annotate ``text`` as ``str``, but at the same time, assign a :class:`~ext.commands.ParamInfo` instance to it.
That's the thing. When your editor type-checks your (any library's) code, it would normally complain if you tried to do the above, because
you're trying to assign a ``ParamInfo`` to a ``str`` - however, since the library declares ``Param``'s return type as ``Any``, the type-checker accepts
your code, because ``str`` (and any type) is a subtype of ``Any``.

The same thing applies to :func:`~ext.commands.inject` and :func:`~ext.commands.injection`.
