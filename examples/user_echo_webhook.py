import os

import disnake
from disnake.ext import commands

description = """This is a script wherein the user can input
                 a UserID as well as message content, and the
                 bot will create a webhook to "impersonate"
                 specified user, so to speak."""

# Not limiting the intents, since this is an example - set this accordingly.
intents = disnake.Intents.all()

client = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"), description=description, intents=intents
)


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")


@client.command()
@commands.has_permissions(
    administrator=True
)  # To make sure that not everyone can use this command.
async def userecho(ctx: commands.Context, member: disnake.Member, *, content):

    await ctx.message.delete()  # We don't want users to see who initiated the command, to make it more realistic :P

    # We fetch the channel's webhooks.
    channel = ctx.channel
    if not isinstance(channel, disnake.TextChannel):
        return
    channel_webhooks = await channel.webhooks()

    # We check if the bot's webhook already exists in the channel.
    for webhook in channel_webhooks:
        # We will check if the creator of the webhook is the same as the bot, and if the name is the same.
        if webhook.user == client.user and webhook.name == "Bot Webhook":
            break
    else:
        # If the webhook does not exist, it will be created.
        webhook = await channel.create_webhook(name="Bot Webhook")

    # Finally, sending the message via the webhook, using the user's display name and avatar.
    await webhook.send(
        content=content, username=member.display_name, avatar_url=member.display_avatar.url
    )

    # Note: This method cannot impersonate the member's roles, since it works using webhooks.


client.run(os.getenv("BOT_TOKEN"))
