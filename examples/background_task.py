import os

import disnake
from disnake.ext import tasks


class MyClient(disnake.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # an attribute we can access from our task
        self.counter = 0

        # start the task to run in the background
        self.my_background_task.start()

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    @tasks.loop(seconds=60)  # task runs every 60 seconds
    async def my_background_task(self):
        self.counter += 1
        await self.channel.send(str(self.counter))

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in
        channel = self.get_channel(1234567)  # channel ID goes here
        if not isinstance(channel, disnake.TextChannel):
            raise ValueError("Invalid channel")

        self.channel = channel


client = MyClient()
client.run(os.getenv("BOT_TOKEN"))
