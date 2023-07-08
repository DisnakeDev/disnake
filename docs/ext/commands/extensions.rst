.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

.. _ext_commands_extensions:

Extensions
==========

There comes a time in the bot development when you want to extend the bot functionality at run-time and quickly unload and reload code (also called hot-reloading). The command framework comes with this ability built-in, with a concept called **extensions**.

Primer
------

An extension at its core is a python file with an entry point called ``setup``. This setup must be a plain Python function (not a coroutine). It takes a single parameter -- the :class:`~.commands.Bot` that loads the extension.

An example extension looks like this:

.. code-block:: python3
    :caption: hello.py
    :emphasize-lines: 7,8

    from disnake.ext import commands

    @commands.command()
    async def hello(ctx):
        await ctx.send(f'Hello {ctx.author.display_name}.')

    def setup(bot):
        bot.add_command(hello)

In this example we define a simple command, and when the extension is loaded this command is added to the bot. Now the final step to this is loading the extension, which we do by calling :meth:`.Bot.load_extension`. To load this extension we call ``bot.load_extension('hello')``.

.. admonition:: Cogs
    :class: helpful

    Extensions are usually used in conjunction with cogs. To read more about them, check out the documentation, :ref:`ext_commands_cogs`.

.. note::

    Extension paths are ultimately similar to the import mechanism. What this means is that if there is a folder, then it must be dot-qualified. For example to load an extension in ``plugins/hello.py`` then we use the string ``plugins.hello``.

Reloading
---------

When you make a change to the extension and want to reload the references, the library comes with a function to do this for you, :meth:`.Bot.reload_extension`.

.. code-block:: python3

    >>> bot.reload_extension('hello')

Once the extension reloads, any changes that we did will be applied. This is useful if we want to add or remove functionality without restarting our bot. If an error occurred during the reloading process, the bot will pretend as if the reload never happened.

Cleaning Up
-----------

Although rare, sometimes an extension needs to clean-up or know when it's being unloaded. For cases like these, there is another entry point named ``teardown`` which is similar to ``setup`` except called when the extension is unloaded.

.. code-block:: python3
    :caption: basic_ext.py

    def setup(bot):
        print('I am being loaded!')

    def teardown(bot):
        print('I am being unloaded!')

.. _ext_commands_extensions_load:

Loading multiple extensions
-----------------------------

Commonly, you might have a package/folder that contains several modules.
Instead of manually loading them one by one, you can use :meth:`.Bot.load_extensions` to load the entire package in one sweep.

Consider the following directory structure:

.. code-block::

    my_bot/
    ├─── cogs/
    │    ├─── admin.py
    │    ├─── fun.py
    │    └─── other_complex_thing/
    │         ├─── __init__.py (contains setup)
    │         ├─── data.py
    │         └─── models.py
    └─── main.py

Now, you could call :meth:`.Bot.load_extension` separately on ``cogs.admin``, ``cogs.fun``, and ``cogs.other_complex_thing``;
however, if you add a new extension, you'd need to once again load it separately.

Instead, you can use ``bot.load_extensions("my_bot.cogs")`` (or ``.load_extensions(".cogs", package=__package__)``)
to load all of them automatically, without any extra work required.

Customization
+++++++++++++++

To adjust the loading process, for example to handle exceptions that may occur, use :meth:`.Bot.find_extensions`.
This is also what :meth:`.Bot.load_extensions` uses internally.

As an example, one could load extensions like this:

.. code-block:: python3

    for extension in bot.find_extensions("my_bot.cogs"):
        try:
            bot.load_extension(extension)
        except commands.ExtensionError as e:
            logger.warning(f"Failed to load extension {extension}: {e}")

Discovery
+++++++++++

:meth:`.Bot.find_extensions` (and by extension, :meth:`.Bot.load_extensions`) discover modules/extensions
similar to :func:`py:pkgutil.walk_packages`; the given root package name is resolved,
and submodules/-packages are iterated through recursively.

If a package has a ``setup`` function (similar to ``my_bot.cogs.other_complex_thing`` above),
it won't be traversed further, i.e. ``data.py`` and ``models.py`` in the example won't be considered separate extensions.

Namespace packages (see `PEP 420 <https://peps.python.org/pep-0420/>`__) are not supported (other than
the provided root package), meaning every subpackage must have an ``__init__.py`` file.
