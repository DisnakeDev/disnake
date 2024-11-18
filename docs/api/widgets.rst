.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Widgets
=======

This section documents everything related to widgets — dynamically
generated elements which show basic info about your server and invites to join it easily,
which can be displayed on websites.

Discord Models
---------------

Widget
~~~~~~~

.. attributetable:: Widget

.. autoclass:: Widget()
    :members:

WidgetSettings
~~~~~~~~~~~~~~

.. attributetable:: WidgetSettings

.. autoclass:: WidgetSettings()
    :members:

WidgetChannel
~~~~~~~~~~~~~

.. attributetable:: WidgetChannel

.. autoclass:: WidgetChannel()
    :members:

WidgetMember
~~~~~~~~~~~~

.. attributetable:: WidgetMember

.. autoclass:: WidgetMember()
    :members:
    :inherited-members:
    :exclude-members: global_name, public_flags, default_avatar, banner, accent_colour, accent_color, colour, color, mention, created_at, mentioned_in, avatar_decoration

Enumerations
------------

WidgetStyle
~~~~~~~~~~~

.. autoclass:: WidgetStyle()
    :members:
