.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

.. _disnake_api_index:

API Reference
=============

The full API Reference can be found by viewing the individual pages in the sidebar or by scrolling to the bottom of this page.

Logging Configuration
----------------------

.. note::

    This module uses the Python logging module to log diagnostic and errors
    in an output independent way.  If the logging module is not configured,
    these logs will not be output anywhere.  See :ref:`logging_setup` for
    more information on how to set up and use the logging module with
    disnake.

.. _disnake_abc:

Abstract Base Classes
---------------------

An :term:`abstract base class` (also known as an ``abc``) is a class that models can inherit
to get their behaviour. **Abstract base classes should not be instantiated**.
They are mainly there for usage with :func:`isinstance` and :func:`issubclass`\.

This library has a module related to abstract base classes, in which all the ABCs are subclasses of
:class:`typing.Protocol` - :ref:`disnake_api_abc`.

.. _discord_model:

Discord Models
--------------

Models are classes that are received from Discord and are not meant to be created by
the user of the library.

.. danger::

    Classes marked as models are **not intended to be created by users** and are also
    **read-only**.

    For example, this means that you should not make your own :class:`User` instances
    nor should you modify the :class:`User` instance yourself.

    If you want to get one of these model classes instances they'd have to be through
    the cache, and a common way of doing so is through the :func:`utils.find` function
    or attributes of model classes that you receive from the :ref:`Events <disnake_api_events>`.

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

.. _discord_enum:

Enumerations
------------

The API provides some enumerations for certain types of values to avoid the API
from being typed as literals in case the values change in the future.

All enumerations are subclasses of an internal class which mimics the behaviour
of :class:`enum.Enum`.

Documents
---------

.. toctree::
    :maxdepth: 1

    abc
    activities
    app_commands
    app_info
    audit_logs
    automod
    ui
    channels
    clients
    components
    emoji
    events
    exceptions
    guilds
    guild_scheduled_events
    integrations
    interactions
    invites
    localization
    members
    messages
    misc
    permissions
    roles
    stage_instances
    stickers
    users
    utilities
    voice
    webhooks
    widgets
