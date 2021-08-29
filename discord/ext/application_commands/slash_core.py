from typing import Dict, TYPE_CHECKING
from .base_core import InvokableApplicationCommand


if TYPE_CHECKING:
    from discord.interactions import ApplicationCommandInteraction


class InvokableSlashCommand(InvokableApplicationCommand):
    def __init__(self, func, *, name: str = None, connectors: Dict[str, str] = None, **kwargs):
        super().__init__(func, name=name, **kwargs)
        self.connectors: Dict[str, str] = connectors

    async def invoke(self, interaction: ApplicationCommandInteraction):
        pass


class SubCommandGroup(InvokableApplicationCommand):
    def __init__(self, func, *, name: str = None, **kwargs):
        super().__init__(func, name=name, **kwargs)
        self.children = {}
        # self.option = Option(
        #     name=self.name,
        #     description="-",
        #     type=Type.SUB_COMMAND_GROUP,
        #     options=[]
        # )

    def sub_command(self, name: str = None, description: str = None, options: list = None, connectors: dict = None, **kwargs):
        """
        A decorator that creates a subcommand in the
        subcommand group.
        Parameters are the same as in :class:`CommandParent.sub_command`
        """
        def decorator(func):
            new_func = SubCommand(
                func,
                name=name,
                description=description,
                options=options,
                connectors=connectors,
                **kwargs
            )
            self.children[new_func.name] = new_func
            self.option.options.append(new_func.option)
            return new_func
        return decorator


class SubCommand(InvokableApplicationCommand):
    def __init__(
        self,
        func,
        *,
        name: str = None,
        description: str = None,
        options: list = None,
        connectors: Dict[str, str] = None,
        **kwargs
    ):
        super().__init__(func, name=name, connectors=connectors, **kwargs)
        # self.option = Option(
        #     name=self.name,
        #     description=description or "-",
        #     type=Type.SUB_COMMAND,
        #     options=options
        # )
