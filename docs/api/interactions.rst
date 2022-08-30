.. currentmodule:: disnake

Interactions
============

This sections documents everything related to interactions - special type of webhooks used for communication between user and client.
Currently the only things Discord sends interactions for are message components and application commands.

Classes
-------

Interaction
~~~~~~~~~~~~

.. attributetable:: Interaction

.. autoclass:: Interaction()
    :members:
    :inherited-members:

ApplicationCommandInteraction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationCommandInteraction

.. autoclass:: ApplicationCommandInteraction()
    :members:
    :inherited-members:

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

ModalInteraction
~~~~~~~~~~~~~~~~

.. attributetable:: ModalInteraction

.. autoclass:: ModalInteraction()
    :members:
    :inherited-members:

InteractionResponse
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: InteractionResponse

.. autoclass:: InteractionResponse()
    :members:

InteractionMessage
~~~~~~~~~~~~~~~~~~~

.. attributetable:: InteractionMessage

.. autoclass:: InteractionMessage()
    :members:
    :inherited-members:

Data Classes
------------

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

ApplicationCommandInteractionDataResolved
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: ApplicationCommandInteractionDataResolved

.. autoclass:: ApplicationCommandInteractionDataResolved()
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

InteractionReference
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: InteractionReference

.. autoclass:: InteractionReference
    :members:

Enumerations
------------

InteractionType
~~~~~~~~~~~~~~~

.. class:: InteractionType

    |discord_enum|

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

    |discord_enum|

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

.. function:: on_application_command(interaction)

    |discord_event|

    Called when an application command is invoked.

    .. warning::

        This is a low level function that is not generally meant to be used.
        Consider using :class:`~ext.commands.Bot` or :class:`~ext.commands.InteractionBot` instead.

    .. warning::

        If you decide to override this event and are using :class:`~disnake.ext.commands.Bot` or related types,
        make sure to call :func:`Bot.process_application_commands <disnake.ext.commands.Bot.process_application_commands>`
        to ensure that the application commands are processed.

    .. versionadded:: 2.0

    :param interaction: The interaction object.
    :type interaction: :class:`ApplicationCommandInteraction`

.. function:: on_application_command_autocomplete(interaction)

    |discord_event|

    Called when an application command autocomplete is called.

    .. warning::

        This is a low level function that is not generally meant to be used.
        Consider using :class:`~ext.commands.Bot` or :class:`~ext.commands.InteractionBot` instead.

    .. warning::
        If you decide to override this event and are using :class:`~disnake.ext.commands.Bot` or related types,
        make sure to call :func:`Bot.process_app_command_autocompletion <disnake.ext.commands.Bot.process_app_command_autocompletion>`
        to ensure that the application command autocompletion is processed.

    .. versionadded:: 2.0

    :param interaction: The interaction object.
    :type interaction: :class:`ApplicationCommandInteraction`

.. function:: on_button_click(interaction)

    |discord_event|

    Called when a button is clicked.

    .. versionadded:: 2.0

    :param interaction: The interaction object.
    :type interaction: :class:`MessageInteraction`

.. function:: on_dropdown(interaction)

    |discord_event|

    Called when a select menu is clicked.

    .. versionadded:: 2.0

    :param interaction: The interaction object.
    :type interaction: :class:`MessageInteraction`

.. function:: on_interaction(interaction)

    |discord_event|

    Called when an interaction happened.

    This currently happens due to application command invocations or components being used.

    .. warning::

        This is a low level function that is not generally meant to be used.

    .. versionadded:: 2.0

    :param interaction: The interaction object.
    :type interaction: :class:`Interaction`

.. function:: on_message_interaction(interaction)

    |discord_event|

    Called when a message interaction happened.

    This currently happens due to components being used.

    .. versionadded:: 2.0

    :param interaction: The interaction object.
    :type interaction: :class:`MessageInteraction`

.. function:: on_modal_submit(interaction)

    |discord_event|

    Called when a modal is submitted.

    .. versionadded:: 2.4

    :param interaction: The interaction object.
    :type interaction: :class:`ModalInteraction`
