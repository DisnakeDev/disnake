# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "click",
# ]
# ///
from __future__ import annotations

import click


@click.command()
@click.argument("guild_id", required=False)
def bootstrap(guild_id: str | None) -> None:
    """Disnake has e2e integration testing with the Discord API.
    This script serves to set up a full Guild for testing.
    """
