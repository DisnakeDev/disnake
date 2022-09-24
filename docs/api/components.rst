.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

.. _disnake_components:

Message Components
==================

This section documents everything related to
`message components <https://discord.com/developers/docs/interactions/message-components>`_ \
- Discord feature which allows bot developers to create their own component-based UIs right inside Discord.

.. note::

    Classes listed below are not meant to be created by user and are only recieved from the API.
    For constructible version see :ref:`Bot UI Kit <disnake_ui_kit>`.

Classes
-------

Component
~~~~~~~~~

.. attributetable:: Component

.. autoclass:: Component()
    :members:

ActionRow
~~~~~~~~~

.. attributetable:: ActionRow

.. autoclass:: ActionRow()
    :members:

Button
~~~~~~

.. attributetable:: Button

.. autoclass:: Button()
    :members:
    :inherited-members:

SelectMenu
~~~~~~~~~~

.. attributetable:: SelectMenu

.. autoclass:: SelectMenu()
    :members:
    :inherited-members:

SelectOption
~~~~~~~~~~~~~

.. attributetable:: SelectOption

.. autoclass:: SelectOption
    :members:

TextInput
~~~~~~~~~

.. attributetable:: TextInput

.. autoclass:: TextInput()
    :members:
    :inherited-members:

Enumerations
------------

ComponentType
~~~~~~~~~~~~~

.. class:: ComponentType

    |discord_enum|

    Represents the component type of a component.

    .. versionadded:: 2.0

    .. attribute:: action_row

        Represents the group component which holds different components in a row.
    .. attribute:: button

        Represents a button component.
    .. attribute:: select

        Represents a select component.
    .. attribute:: text_input

        Represents a text input component.

ButtonStyle
~~~~~~~~~~~

.. class:: ButtonStyle

    |discord_enum|

    Represents the style of the button component.

    .. versionadded:: 2.0

    .. attribute:: primary

        Represents a blurple button for the primary action.
    .. attribute:: secondary

        Represents a grey button for the secondary action.
    .. attribute:: success

        Represents a green button for a successful action.
    .. attribute:: danger

        Represents a red button for a dangerous action.
    .. attribute:: link

        Represents a link button.

    .. attribute:: blurple

        An alias for :attr:`primary`.
    .. attribute:: grey

        An alias for :attr:`secondary`.
    .. attribute:: gray

        An alias for :attr:`secondary`.
    .. attribute:: green

        An alias for :attr:`success`.
    .. attribute:: red

        An alias for :attr:`danger`.
    .. attribute:: url

        An alias for :attr:`link`.

TextInputStyle
~~~~~~~~~~~~~~

.. class:: TextInputStyle

    |discord_enum|

    Represents a style of the text input component.

    .. versionadded:: 2.4

    .. attribute:: short

        Represents a single-line text input component.
    .. attribute:: paragraph

        Represents a multi-line text input component.
    .. attribute:: single_line

        An alias for :attr:`short`.
    .. attribute:: multi_line

        An alias for :attr:`paragraph`.
    .. attribute:: long

        An alias for :attr:`paragraph`.
