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
    :exclude-members: add_select

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

StringSelect
~~~~~~~~~~~~

.. attributetable:: StringSelect

.. autoclass:: StringSelect
    :members:
    :inherited-members:

ChannelSelect
~~~~~~~~~~~~~

.. attributetable:: ChannelSelect

.. autoclass:: ChannelSelect
    :members:
    :inherited-members:

MentionableSelect
~~~~~~~~~~~~~~~~~

.. attributetable:: MentionableSelect

.. autoclass:: MentionableSelect
    :members:
    :inherited-members:

RoleSelect
~~~~~~~~~~

.. attributetable:: RoleSelect

.. autoclass:: RoleSelect
    :members:
    :inherited-members:

UserSelect
~~~~~~~~~~

.. attributetable:: UserSelect

.. autoclass:: UserSelect
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
    :decorator:

.. autofunction:: string_select(cls=StringSelect, *, custom_id=..., placeholder=None, min_values=1, max_values=1, options=..., disabled=False, row=None)
    :decorator:

.. autofunction:: channel_select(cls=ChannelSelect, *, custom_id=..., placeholder=None, min_values=1, max_values=1, disabled=False, channel_types=None, row=None)
    :decorator:

.. autofunction:: mentionable_select(cls=MentionableSelect, *, custom_id=..., placeholder=None, min_values=1, max_values=1, disabled=False, row=None)
    :decorator:

.. autofunction:: role_select(cls=RoleSelect, *, custom_id=..., placeholder=None, min_values=1, max_values=1, disabled=False, row=None)
    :decorator:

.. autofunction:: user_select(cls=UserSelect, *, custom_id=..., placeholder=None, min_values=1, max_values=1, disabled=False, row=None)
    :decorator:
