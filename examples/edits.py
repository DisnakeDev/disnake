import asyncio

import disnake


class MyClient(disnake.Client):
    async def on_ready(self) -> None:
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def on_message(self, message: disnake.Message) -> None:
        if message.content.startswith("!editme"):
            channel_message = await message.channel.send("10")
            await asyncio.sleep(3.0)
            await channel_message.edit(content="40")

    async def on_message_edit(self, before: disnake.Message, after: disnake.Message) -> None:
        await before.channel.send(
            f"**{before.author}** edited their message:\n"
            f"{before.content} -> {after.content}"
        )


client = MyClient()
client.run("token")
