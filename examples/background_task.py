# SPDX-License-Identifier: MIT

"""An example showing how to regularly run a task in the background."""

import os

import disnake
from disnake.ext import tasks

CHANNEL_ID = 1234567  # channel ID goes here


class MyClient(disnake.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # an attribute we can access from our task
        self.counter = 0

        # start the task to run in the background
        self.my_background_task.start()

    @tasks.loop(seconds=60)  # task runs every 60 seconds
    async def my_background_task(self):
        self.counter += 1
        await self.channel.send(str(self.counter))

    # called before the task/loop starts running
    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the cache is populated

        channel = self.get_channel(CHANNEL_ID)
        if not isinstance(channel, disnake.TextChannel):
            raise TypeError("Invalid channel")

        self.channel = channel

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})\n------")


if __name__ == "__main__":
    client = MyClient()
    client.run(os.getenv("BOT_TOKEN"))
