.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake.ui

.. _disnake_ui_kit:

Bot UI Kit
==========

This section documents everything related to the Discord Bot UI Kit - a group of helper functions and classes that aid in making :ref:`component-based <disnake_components>` UIs.

Classes
-------

View
~~~~

.. attributetable:: View

.. autoclass:: View
    :members:

ActionRow
~~~~~~~~~

.. attributetable:: ActionRow

.. autoclass:: ActionRow
    :members:

Item
~~~~

.. attributetable:: Item

.. autoclass:: Item
    :members:

WrappedComponent
~~~~~~~~~~~~~~~~

.. attributetable:: WrappedComponent

.. autoclass:: WrappedComponent
    :members:

Button
~~~~~~

.. attributetable:: Button

.. autoclass:: Button
    :members:
    :inherited-members:

BaseSelect
~~~~~~~~~~

.. attributetable:: BaseSelect

.. autoclass:: BaseSelect
   :members:
   :inherited-members:

Select
~~~~~~

.. attributetable:: Select

.. autoclass:: Select
    :members:
    :inherited-members:


Modal
~~~~~

.. attributetable:: Modal

.. autoclass:: Modal
    :members:

TextInput
~~~~~~~~~

.. attributetable:: TextInput

.. autoclass:: TextInput
    :members:

Functions
---------

.. autofunction:: button(cls=Button, *, style=ButtonStyle.secondary, label=None, disabled=False, custom_id=..., url=None, emoji=None, row=None)

.. autofunction:: select(cls=Select, *, custom_id=..., placeholder=None, min_values=1, max_values=1, options=..., disabled=False, row=None)
