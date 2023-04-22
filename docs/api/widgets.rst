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
    :exclude-members: public_flags, default_avatar, banner, accent_colour, accent_color, colour, color, mention, created_at, mentioned_in

Enumerations
------------

WidgetStyle
~~~~~~~~~~~

.. class:: WidgetStyle

    Represents the supported widget image styles.

    .. versionadded:: 2.5

    .. attribute:: shield

        A shield style image with a Discord icon and the online member count.

    .. attribute:: banner1

        A large image with guild icon, name and online member count and a footer.

    .. attribute:: banner2

        A small image with guild icon, name and online member count.

    .. attribute:: banner3

        A large image with guild icon, name and online member count and a footer,
        with a "Chat Now" label on the right.

    .. attribute:: banner4

        A large image with a large Discord logo, guild icon, name and online member count,
        with a "Join My Server" label at the bottom.
