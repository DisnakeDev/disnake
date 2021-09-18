import disnake
from disnake.ext import commands

description = """This is a script wherein the user can input 
                 a UserID as well as message content, and the
                 bot will create a webhook to "impersonate" 
                 specified user, so to speak."""

intents = disnake.Intents.all() # Not limiting the permissions, since this is an example - set this accordingly.

client = commands.Bot(command_prefix = "!", description = description, intents = intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

@client.command()
@commands.has_permissions(administrator=True) # To make sure that not everyone can use this command.
async def userecho(ctx, member: disnake.Member, *, content):
  
    await ctx.message.delete() # We don't want users to see who initiated the command, to make it more realistic :P
    
    # We check if the bot's webhook already exists in the channel.
    webhooks = await ctx.channel.webhooks()
    webhook = disnake.utils.get(webhook, "Bot's Webhook")
    
    # If the webhook does not exist, it will be created.
    if webhook is None:
      webhook = await ctx.channel.create_webhook(name="Bot's Webhook", reason="Bot Webhook") 
    
    # Finally, sending the message via the webhook - the bot will fetch the user's display name and avatar.
    # NOTE: This method cannot impersonate the member's roles, since it works using webhooks.
    await new_webhook.send(content=content, username=member.display_name, avatar_url=member.avatar)
    
client.run("YOUR_TOKEN_HERE")
