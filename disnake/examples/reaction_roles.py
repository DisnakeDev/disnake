# SPDX-License-Identifier: MIT

"""A role self-assign example, using reactions."""

import os

import disnake

ROLE_MESSAGE_ID = 1234567  # message ID goes here

EMOJI_TO_ROLE = {
    disnake.PartialEmoji(name="🔴"): 123,  # ID of the role associated with unicode emoji '🔴'.
    disnake.PartialEmoji(name="🟡"): 456,  # ID of the role associated with unicode emoji '🟡'.
    disnake.PartialEmoji(name="green"): 789,  # ID of the role associated with a partial emoji's ID.
}


class MyClient(disnake.Client):
    async def on_raw_reaction_add(self, payload: disnake.RawReactionActionEvent):
        """Gives a role based on a reaction emoji."""
        if payload.guild_id is None or payload.member is None:
            return

        # Make sure that the message the user is reacting to is the one we care about.
        if payload.message_id != ROLE_MESSAGE_ID:
            return

        guild = self.get_guild(payload.guild_id)
        if guild is None:
            # Check if we're still in the guild and it's cached.
            return

        try:
            role_id = EMOJI_TO_ROLE[payload.emoji]
        except KeyError:
            # If the emoji isn't the one we care about then exit as well.
            return

        role = guild.get_role(role_id)
        if role is None:
            # Make sure the role still exists and is valid.
            return

        try:
            # Finally, add the role.
            await payload.member.add_roles(role)
        except disnake.HTTPException:
            # If we want to do something in case of errors we'd do it here.
            pass

    async def on_raw_reaction_remove(self, payload: disnake.RawReactionActionEvent):
        """Removes a role based on a reaction emoji."""
        if payload.guild_id is None:
            return

        # Make sure that the message the user is reacting to is the one we care about.
        if payload.message_id != ROLE_MESSAGE_ID:
            return

        guild = self.get_guild(payload.guild_id)
        if guild is None:
            # Check if we're still in the guild and it's cached.
            return

        try:
            role_id = EMOJI_TO_ROLE[payload.emoji]
        except KeyError:
            # If the emoji isn't the one we care about then exit as well.
            return

        role = guild.get_role(role_id)
        if role is None:
            # Make sure the role still exists and is valid.
            return

        # The payload for `on_raw_reaction_remove` does not provide `.member`
        # so we must get the member ourselves from the payload's `.user_id`.
        member = guild.get_member(payload.user_id)
        if member is None:
            # Make sure the member still exists and is valid.
            return

        try:
            # Finally, remove the role.
            await member.remove_roles(role)
        except disnake.HTTPException:
            # If we want to do something in case of errors we'd do it here.
            pass

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})\n------")


intents = disnake.Intents.default()
intents.members = True

if __name__ == "__main__":
    client = MyClient(intents=intents)
    client.run(os.getenv("BOT_TOKEN"))
