.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Glossary
========

This page explain various terms used in documentation.

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
:class:`typing.Protocol` - :ref:`disnake_abcs_ref`.

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
    or attributes of model classes that you receive from the :ref:`Events <discord_api_events>`.

.. note::

    Nearly all models have :ref:`py:slots` defined which means that it is
    impossible to have dynamic attributes on them.

.. _discord_enum:

Enumerations
------------

The API provides some enumerations for certain types of strings to avoid the API
from being stringly typed in case the strings change in the future.

All enumerations are subclasses of an internal class which mimics the behaviour
of :class:`enum.Enum`.

