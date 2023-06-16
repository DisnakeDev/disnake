# SPDX-License-Identifier: MIT

"""An example showing how to reply to received messages."""

import os

import disnake


class MyClient(disnake.Client):
    async def on_message(self, message: disnake.Message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith("!hello"):
            await message.reply("Hello!", mention_author=True)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})\n------")


intents = disnake.Intents.default()
intents.message_content = True

if __name__ == "__main__":
    client = MyClient(intents=intents)
    client.run(os.getenv("BOT_TOKEN"))
