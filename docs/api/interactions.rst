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

Enumerations
------------

InteractionType
~~~~~~~~~~~~~~~

.. class:: InteractionType

    Specifies the type of :class:`Interaction`.

    .. versionadded:: 2.0

    .. attribute:: ping

        Represents Discord pinging to see if the interaction response server is alive.
    .. attribute:: application_command

        Represents an application command interaction.
    .. attribute:: component

        Represents a component based interaction, i.e. using the Discord Bot UI Kit.
    .. attribute:: application_command_autocomplete

        Represents an application command autocomplete interaction.
    .. attribute:: modal_submit

        Represents a modal submit interaction.

InteractionResponseType
~~~~~~~~~~~~~~~~~~~~~~~

.. class:: InteractionResponseType

    Specifies the response type for the interaction.

    .. versionadded:: 2.0

    .. attribute:: pong

        Pongs the interaction when given a ping.

        See also :meth:`InteractionResponse.pong`
    .. attribute:: channel_message

        Respond to the interaction with a message.

        See also :meth:`InteractionResponse.send_message`
    .. attribute:: deferred_channel_message

        Responds to the interaction with a message at a later time.

        See also :meth:`InteractionResponse.defer`
    .. attribute:: deferred_message_update

        Acknowledges the component interaction with a promise that
        the message will update later (though there is no need to actually update the message).

        See also :meth:`InteractionResponse.defer`
    .. attribute:: message_update

        Responds to the interaction by editing the message.

        See also :meth:`InteractionResponse.edit_message`
    .. attribute:: application_command_autocomplete_result

        Responds to the autocomplete interaction with suggested choices.

        See also :meth:`InteractionResponse.autocomplete`
    .. attribute:: modal

        Responds to the interaction by displaying a modal.

        See also :meth:`InteractionResponse.send_modal`

Events
------

- :func:`on_application_command(interaction) <disnake.on_application_command>`
- :func:`on_application_command_autocomplete(interaction) <disnake.on_application_command_autocomplete>`
- :func:`on_button_click(interaction) <disnake.on_button_click>`
- :func:`on_dropdown(interaction) <disnake.on_dropdown>`
- :func:`on_interaction(interaction) <disnake.on_interaction>`
- :func:`on_message_interaction(interaction) <disnake.on_message_interaction>`
- :func:`on_modal_submit(interaction) <disnake.on_modal_submit>`
