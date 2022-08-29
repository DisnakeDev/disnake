.. currentmodule:: disnake

API Reference
=============

The following documents outline the API of disnake.

.. note::

    This module uses the Python logging module to log diagnostic and errors
    in an output independent way.  If the logging module is not configured,
    these logs will not be output anywhere.  See :ref:`logging_setup` for
    more information on how to set up and use the logging module with
    disnake.

.. _version_related:

Version Related Info
--------------------

There are two main ways to query version information about the library. For guarantees, check :ref:`version_guarantees`.

.. data:: version_info

    A named tuple that is similar to :obj:`py:sys.version_info`.

    Just like :obj:`py:sys.version_info` the valid values for ``releaselevel`` are
    'alpha', 'beta', 'candidate' and 'final'.

.. data:: __version__

    A string representation of the version. e.g. ``'1.0.0rc1'``. This is based
    off of :pep:`440`.

.. _discord_event:

Events
------

Most of the :class:`Client` application cycle is based on *events* - special "notifications" usually sent by Discord
to notify client about certain actions like message deletion, ``:mmlol:`` emoji creation, member nickname update, etc.
This allows you to respond to certain actions by making another actions, about which Discord will notify other
connected clients (i.e., other bots and users). This library provides two main ways to register an
*event handler* - a special function which will *watch* to certain types of events and allow you to do anything you
want in response to those events.

The first way is through the use of the :meth:`Client.event` decorator: ::

    import disnake

    client = disnake.Client()
    
    @client.event
    async def on_message(message):
        if message.author.bot:
            return
        
        if message.content.startswith('$hello'):
            await message.reply(f'Hello, {message.author}!')

The second way is through subclassing :class:`Client` and
overriding the specific events. For example: ::

    import disnake

    class MyClient(disnake.Client):
        async def on_message(self, message):
            if message.author.bot:
                return

            if message.content.startswith('$hello'):
                await message.reply(f'Hello, {message.author}!')

The above pieces of code are essentially equal, and both respond with "Hello, {message author's username here}!" message
when a user sends "$hello" message.

.. warning::

    Event handlers described here are a bit different from :class:`~ext.commands.Bot`'s *event listeners*.
    :class:`Client`'s event handlers are *unique*: you can't have two :func:`on_message`, two
    :func:`on_member_ban` etc. With :class:`~ext.commands.Bot` however, you can have as much *listeners*
    of the same type as you want.
    
    Please also note that using :meth:`Bot.event() <disnake.ext.commands.Bot.event>` decorator is the same as using :class:`Client`'s
    :meth:`~Client.event` (since :class:`~ext.commands.Bot` subclasses :class:`Client`) and does not allow to listen/watch
    for multiple events of the same type. Consider using :meth:`Bot.listen() <disnake.ext.commands.Bot.listen>` for that.

.. note::

    Events can be sent not only by Discord. For instance, if you use :ref:`commands extension <discord_ext_commands>`,
    you'll also receive :ref:`various events <ext_commands_api_events>` related to your commands' execution process.

If an event handler raises an exception, :func:`on_error` will be called
to handle it, which defaults to print a traceback and ignoring the exception.

.. warning::

    All the events must be a |coroutine_link|_. If they aren't, then you might get unexpected
    errors. In order to turn a function into a coroutine they must be ``async def``
    functions.

.. _discord_enum:

Enumerations
------------

The API provides some enumerations for certain types of strings to avoid the API
from being stringly typed in case the strings change in the future.

All enumerations are subclasses of an internal class which mimics the behaviour
of :class:`enum.Enum`.

.. _discord_model:

Discord Models
---------------

Models are classes that are received from Discord and are not meant to be created by
the user of the library.

.. danger::

    Classes marked as models are **not intended to be created by users** and are also
    **read-only**.

    For example, this means that you should not make your own :class:`User` instances
    nor should you modify the :class:`User` instance yourself.

    If you want to get one of these model classes instances they'd have to be through
    the cache, and a common way of doing so is through the :func:`utils.find` function
    or attributes of model classes that you receive from the :ref:`Events <discord_event>`.

.. note::

    Nearly all models have :ref:`py:slots` defined which means that it is
    impossible to have dynamic attributes on them.

.. _data_class:

Data Classes
------------

Some classes are just there to be data containers. We call them *data classes*.

Unlike :ref:`models <discord_model>` you are allowed to create
most of these yourself, even if they can also be used to hold attributes.

Nearly all data classes have :ref:`py:slots` defined which means that it is
impossible to have dynamic attributes on them.

The only exception to this rule is :class:`Object`, which is made with
dynamic attributes in mind.

.. _discord_abc:

Abstract Base Classes
---------------------

An :term:`abstract base class` (also known as an ``abc``) is a class that models can inherit
to get their behaviour. **Abstract base classes should not be instantiated**.
They are mainly there for usage with :func:`isinstance` and :func:`issubclass`\.

This library has a module related to abstract base classes, in which all the ABCs are subclasses of
:class:`typing.Protocol` - :ref:`discord_abcs_ref`.

Documents
---------

.. toctree::
    :maxdepth: 1

    Abstract Base Classes <abc.rst>
    Activities <activity.rst>
    Application Info <app_info.rst>
    Application Commands <app_commands.rst>
    Audit Logs <audit_log.rst>
    AutoMod <automod.rst>
    Bot UI Kit <ui.rst>
    Channels <channels.rst>
    Clients <client.rst>
    Emoji <emoji.rst>
    Exceptions and Warnings <exceptions.rst>
    Guild <guild.rst>
    Guild Scheduled Event <guild_scheduled_event.rst>
    Integration <integration.rst>
    Interactions <interactions.rst>
    Invite <invite.rst>
    Localization <localization.rst>
    Member <member.rst>
    Message <message.rst>
    Message Components <components.rst>
    Miscellaneous <misc.rst>
    Permissions <permissions.rst>
    Role <role.rst>
    Stage Instance <stage_instance.rst>
    Stickers <sticker.rst>
    User <user.rst>
    Utility functions <utils.rst>
    Voice Related <voice.rst>
    Webhooks <webhook.rst>
    Widget <widget.rst>