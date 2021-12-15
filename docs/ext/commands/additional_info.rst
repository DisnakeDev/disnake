.. currentmodule:: disnake

.. _ext_commands_additional_info:

Additional info
===============

This section contains explanations of some library mechanics which may be useful to know.

.. _app_command_sync:

App command sync
-----------------

If you're using ``ext.commands`` framework for application commands (slash commands, context menus) you should
understand how your commands show up in Discord. If ``sync_commands`` kwarg is set to ``True`` (which is the default value)
the library registers / updates all commands automatically. Based on the application commands defined in your code it decides
which commands should be registered, edited or deleted but there're some edge cases you should keep in mind.

Global registration
+++++++++++++++++++

Registering commands globally may take up to 1 hour, this is an API limitation. You don't have to keep your bot online this whole time though,
it's enough to launch it at least once.

Changing test guilds
++++++++++++++++++++

If you remove some IDs from the ``test_guilds`` kwarg of ``commands.Bot`` (or a similar class) the commands in those guilds
won't be deleted instantly. Instead, they'll be deleted as soon as one of the deprecated commands is invoked. Your bot will send a message
like "This command was incorrectly synced ...".
