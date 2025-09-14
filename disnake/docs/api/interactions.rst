.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Interactions
============

This section documents everything related to interactions, which are used for communication between user and client.
Common examples are message components and application commands.

Discord Models
---------------

Interaction
~~~~~~~~~~~

.. attributetable:: Interaction

.. autoclass:: Interaction()
    :members:
    :inherited-members:
    :exclude-members: original_message, edit_original_message, delete_original_message

    .. method:: original_message

        An alias of :func:`original_response`.

    .. method:: edit_original_message

        An alias of :func:`edit_original_response`.

    .. method:: delete_original_message

        An alias of :func:`delete_original_response`.

ApplicationCommandInteraction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationCommandInteraction

.. autoclass:: ApplicationCommandInteraction()
    :members:
    :inherited-members:
    :exclude-members: original_message, edit_original_message, delete_original_message

    .. method:: original_message

        An alias of :func:`original_response`.

    .. method:: edit_original_message

        An alias of :func:`edit_original_response`.

    .. method:: delete_original_message

        An alias of :func:`delete_original_response`.

GuildCommandInteraction
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: GuildCommandInteraction()

UserCommandInteraction
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: UserCommandInteraction()

MessageCommandInteraction
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: MessageCommandInteraction()

MessageInteraction
~~~~~~~~~~~~~~~~~~

.. attributetable:: MessageInteraction

.. autoclass:: MessageInteraction()
    :members:
    :inherited-members:
    :exclude-members: original_message, edit_original_message, delete_original_message

    .. method:: original_message

        An alias of :func:`original_response`.

    .. method:: edit_original_message

        An alias of :func:`edit_original_response`.

    .. method:: delete_original_message

        An alias of :func:`delete_original_response`.

ModalInteraction
~~~~~~~~~~~~~~~~

.. attributetable:: ModalInteraction

.. autoclass:: ModalInteraction()
    :members:
    :inherited-members:
    :exclude-members: original_message, edit_original_message, delete_original_message

    .. method:: original_message

        An alias of :func:`original_response`.

    .. method:: edit_original_message

        An alias of :func:`edit_original_response`.

    .. method:: delete_original_message

        An alias of :func:`delete_original_response`.

InteractionResponse
~~~~~~~~~~~~~~~~~~~

.. attributetable:: InteractionResponse

.. autoclass:: InteractionResponse()
    :members:

InteractionMessage
~~~~~~~~~~~~~~~~~~

.. attributetable:: InteractionMessage

.. autoclass:: InteractionMessage()
    :members:
    :inherited-members:
    :exclude-members: activity, role_subscription_data

InteractionDataResolved
~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: InteractionDataResolved

.. autoclass:: InteractionDataResolved()
    :members:

ApplicationCommandInteractionData
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationCommandInteractionData

.. autoclass:: ApplicationCommandInteractionData()
    :members:

ApplicationCommandInteractionDataOption
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationCommandInteractionDataOption

.. autoclass:: ApplicationCommandInteractionDataOption()
    :members:

MessageInteractionData
~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: MessageInteractionData

.. autoclass:: MessageInteractionData()
    :members:

ModalInteractionData
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: ModalInteractionData

.. autoclass:: ModalInteractionData()
    :members:

Data Classes
------------

AuthorizingIntegrationOwners
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: AuthorizingIntegrationOwners

.. autoclass:: AuthorizingIntegrationOwners()
    :members:

Enumerations
------------

InteractionType
~~~~~~~~~~~~~~~

.. autoclass:: InteractionType()
    :members:

InteractionResponseType
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: InteractionResponseType()
    :members:

Events
------

- :func:`on_application_command(interaction) <disnake.on_application_command>`
- :func:`on_application_command_autocomplete(interaction) <disnake.on_application_command_autocomplete>`
- :func:`on_button_click(interaction) <disnake.on_button_click>`
- :func:`on_dropdown(interaction) <disnake.on_dropdown>`
- :func:`on_interaction(interaction) <disnake.on_interaction>`
- :func:`on_message_interaction(interaction) <disnake.on_message_interaction>`
- :func:`on_modal_submit(interaction) <disnake.on_modal_submit>`
