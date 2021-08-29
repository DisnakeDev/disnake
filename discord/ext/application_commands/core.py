from typing import Any, Dict, TYPE_CHECKING

from discord.interactions import ApplicationCommandInteraction

__all__ = (
    'ApplicationCommandStore',
)

if TYPE_CHECKING:
    from discord.state import ConnectionState

class ApplicationCommandStore:
    # TODO: Make InvokeableApplicationCommand subclasses
    def __init__(self, state: ConnectionState):
        # command_name: InvokeableApplicationCommand
        self._slash_commands: Dict[str, Any] = {}
        self._user_commands: Dict[str, Any] = {}
        self._message_commands: Dict[str, Any] = {}
        self._state: ConnectionState = state

    def dispatch(self, interaction: ApplicationCommandInteraction):
        app_command_type = interaction.data.type
        app_command_name = interaction.data.name
        if app_command_type == 1:
            app_command = self._slash_commands.get(app_command_name)
        elif app_command_type == 2:
            app_command = self._user_commands.get(app_command_name)
        elif app_command_type == 3:
            app_command = self._message_commands.get(app_command_name)
        if app_command is None:
            return
        app_command.dispatch_interaction(interaction)
