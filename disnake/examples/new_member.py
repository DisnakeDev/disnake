# SPDX-License-Identifier: MIT

"""An example sending welcome messages for newly joined members."""

import os

import disnake


class MyClient(disnake.Client):
    async def on_member_join(self, member: disnake.Member):
        guild = member.guild
        if guild.system_channel:
            to_send = f"Welcome {member.mention} to {guild.name}!"
            await guild.system_channel.send(to_send)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})\n------")


intents = disnake.Intents.default()
intents.members = True

if __name__ == "__main__":
    client = MyClient(intents=intents)
    client.run(os.getenv("BOT_TOKEN"))
