.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake.ui

.. _disnake_api_ui:

Bot UI Kit
==========

This section documents everything related to the Discord Bot UI Kit - a group of helper functions and classes that aid in making :ref:`component-based <disnake_api_components>` UIs.

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

ChannelSelect
~~~~~~~~~~~~~~

.. attributetable:: disnake.ui.ChannelSelect

.. autoclass:: disnake.ui.ChannelSelect
    :members:
    :inherited-members:

.. autofunction:: disnake.ui.channel_select(cls=disnake.ui.ChannelSelect, *, custom_id=..., placeholder=None, min_values=1, max_values=1, disabled=False, channel_types=None, row=None)

MentionableSelect
~~~~~~~~~~~~~~~~~~

.. attributetable:: disnake.ui.MentionableSelect

.. autoclass:: disnake.ui.MentionableSelect
    :members:
    :inherited-members:

.. autofunction:: disnake.ui.mentionable_select(cls=disnake.ui.MentionableSelect, *, custom_id=..., placeholder=None, min_values=1, max_values=1, disabled=False, row=None)

RoleSelect
~~~~~~~~~~~

.. attributetable:: disnake.ui.RoleSelect

.. autoclass:: disnake.ui.RoleSelect
    :members:
    :inherited-members:

.. autofunction:: disnake.ui.role_select(cls=disnake.ui.RoleSelect, *, custom_id=..., placeholder=None, min_values=1, max_values=1, disabled=False, row=None)

StringSelect
~~~~~~~~~~~~~

.. attributetable:: disnake.ui.StringSelect

.. autoclass:: disnake.ui.StringSelect
    :members:
    :inherited-members:

.. autofunction:: disnake.ui.string_select(cls=disnake.ui.StringSelect, *, custom_id=..., placeholder=None, min_values=1, max_values=1, options=..., disabled=False, row=None)

UserSelect
~~~~~~~~~~~

.. attributetable:: disnake.ui.UserSelect

.. autoclass:: disnake.ui.UserSelect
    :members:
    :inherited-members:

.. autofunction:: disnake.ui.user_select(cls=disnake.ui.UserSelect, *, custom_id=..., placeholder=None, min_values=1, max_values=1, disabled=False, row=None)

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
