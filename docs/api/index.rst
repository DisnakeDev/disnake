.. currentmodule:: disnake

.. _disnake_api_index:

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
    or attributes of model classes that you receive from the :ref:`Events <discord_events>`.

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

.. _disnake_abc:

Abstract Base Classes
---------------------

An :term:`abstract base class` (also known as an ``abc``) is a class that models can inherit
to get their behaviour. **Abstract base classes should not be instantiated**.
They are mainly there for usage with :func:`isinstance` and :func:`issubclass`\.

This library has a module related to abstract base classes, in which all the ABCs are subclasses of
:class:`typing.Protocol` - :ref:`disnake_abcs_ref`.

Documents
---------

.. toctree::
    :maxdepth: 1

    Abstract Base Classes <abc.rst>
    Activities <activities.rst>
    Application Info <app_info.rst>
    Application Commands <app_commands.rst>
    Audit Logs <audit_logs.rst>
    AutoMod <automod.rst>
    Bot UI Kit <ui.rst>
    Channels <channels.rst>
    Clients <clients.rst>
    Emoji <emoji.rst>
    Events <events.rst>
    Exceptions and Warnings <exceptions.rst>
    Guilds <guilds.rst>
    Guild Scheduled Events <guild_scheduled_events.rst>
    Integrations <integrations.rst>
    Interactions <interactions.rst>
    Invites <invites.rst>
    Localization <localization.rst>
    Members <members.rst>
    Messages <messages.rst>
    Message Components <components.rst>
    Miscellaneous <misc.rst>
    Permissions <permissions.rst>
    Roles <roles.rst>
    Stage Instances <stage_instances.rst>
    Stickers <stickers.rst>
    Users <users.rst>
    Utility functions <utils.rst>
    Voice Related <voice.rst>
    Webhooks <webhooks.rst>
    Widgets <widgets.rst>
