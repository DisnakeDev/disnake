import disnake
from disnake.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_guild_scheduled_event_create(self, event: disnake.GuildScheduledEvent):
        print("EVENT CREATE")
        print(event.name, event.user_count, event.sku_ids, end="\n")

    @commands.Cog.listener()
    async def on_guild_scheduled_event_update(
        self, before: disnake.GuildScheduledEvent, after: disnake.GuildScheduledEvent
    ):
        print("EVENT UPDATE")
        print(after.guild.scheduled_events, end="\n")  # type: ignore

    @commands.Cog.listener()
    async def on_guild_scheduled_event_delete(self, event: disnake.GuildScheduledEvent):
        print("EVENT DELETE")
        print(event.name, event.user_count, event.sku_ids, end="\n")

    @commands.Cog.listener()
    async def on_raw_guild_scheduled_event_subscribe(
        self, event: disnake.GuildScheduledEvent, user: disnake.User
    ):
        print("EVENT SUBSCRIBE")
        print(event, user)

    @commands.Cog.listener()
    async def on_raw_guild_scheduled_event_unsubscribe(
        self, event: disnake.GuildScheduledEvent, user: disnake.User
    ):
        print("EVENT UNSUBSCRIBE")
        print(event, user)


def setup(bot):
    bot.add_cog(Events(bot))
    print(f"> Extension {__name__} is ready\n")
