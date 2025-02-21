.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

.. _disnake_api_components:

Components
===========

This section documents everything related to
:ddocs:`message components <interactions/message-components>` — a Discord feature
which allows bot developers to create their own component-based UIs right inside Discord.

.. warning::

    Classes listed below are not meant to be created by user and are only recieved from the API.
    For constructible versions, see :ref:`Bot UI Kit <disnake_api_ui>`.

Discord Models
---------------

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

BaseSelectMenu
~~~~~~~~~~~~~~

.. attributetable:: BaseSelectMenu

.. autoclass:: BaseSelectMenu()
    :members:
    :inherited-members:

ChannelSelectMenu
~~~~~~~~~~~~~~~~~

.. attributetable:: ChannelSelectMenu

.. autoclass:: ChannelSelectMenu()
    :members:
    :inherited-members:

MentionableSelectMenu
~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: MentionableSelectMenu

.. autoclass:: MentionableSelectMenu()
    :members:
    :inherited-members:

RoleSelectMenu
~~~~~~~~~~~~~~

.. attributetable:: RoleSelectMenu

.. autoclass:: RoleSelectMenu()
    :members:
    :inherited-members:

StringSelectMenu
~~~~~~~~~~~~~~~~~

.. attributetable:: StringSelectMenu

.. autoclass:: StringSelectMenu()
    :members:
    :inherited-members:

UserSelectMenu
~~~~~~~~~~~~~~

.. attributetable:: UserSelectMenu

.. autoclass:: UserSelectMenu()
    :members:
    :inherited-members:

SelectOption
~~~~~~~~~~~~

.. attributetable:: SelectOption

.. autoclass:: SelectOption
    :members:

SelectDefaultValue
~~~~~~~~~~~~~~~~~~

.. attributetable:: SelectDefaultValue

.. autoclass:: SelectDefaultValue
    :members:

TextInput
~~~~~~~~~

.. attributetable:: TextInput

.. autoclass:: TextInput()
    :members:
    :inherited-members:

Section
~~~~~~~

.. attributetable:: Section

.. autoclass:: Section()
    :members:
    :inherited-members:

TextDisplay
~~~~~~~~~~~

.. attributetable:: TextDisplay

.. autoclass:: TextDisplay()
    :members:
    :inherited-members:

Thumbnail
~~~~~~~~~

.. attributetable:: Thumbnail

.. autoclass:: Thumbnail()
    :members:
    :inherited-members:

MediaGallery
~~~~~~~~~~~~

.. attributetable:: MediaGallery

.. autoclass:: MediaGallery()
    :members:
    :inherited-members:

MediaGalleryItem
~~~~~~~~~~~~~~~~

.. attributetable:: MediaGalleryItem

.. autoclass:: MediaGalleryItem
    :members:

FileComponent
~~~~~~~~~~~~~

.. attributetable:: FileComponent

.. autoclass:: FileComponent()
    :members:
    :inherited-members:

Separator
~~~~~~~~~

.. attributetable:: Separator

.. autoclass:: Separator()
    :members:
    :inherited-members:

Container
~~~~~~~~~

.. attributetable:: Container

.. autoclass:: Container()
    :members:
    :inherited-members:

Enumerations
------------

ComponentType
~~~~~~~~~~~~~

.. autoclass:: ComponentType()
    :members:

ButtonStyle
~~~~~~~~~~~

.. autoclass:: ButtonStyle()
    :members:

TextInputStyle
~~~~~~~~~~~~~~

.. autoclass:: TextInputStyle()
    :members:

SelectDefaultValueType
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: SelectDefaultValueType()
    :members:

SeparatorSpacingSize
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: SeparatorSpacingSize()
    :members:
