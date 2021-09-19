from disnake import Option, OptionChoice, Interaction, Intents
from disnake.ext import commands
from disnake.ext.commands import slash_command

import random

intents = Intents.all()
# In production please choose the intents coresponding to your use case.

# We create the instance of the bot.
bot = commands.Bot(intents=intents)

# For this example we're going to make a rock-paper-scissors game
# which will use OptionChoice as the input.
@slash_command(name='rps', description='Play a game of rock-paper-scissors with the bot.',
    options=[
        Option(name='choice', description='Select your choice for rock-paper-scissors.', choices=[
            OptionChoice(name='Rock', value='rock'),
            OptionChoice(name='Paper', value='paper'),
            OptionChoice(name='Scissors', value='scissors')
        ],
        required=True)  # We're going to make this be a required option.
    ])
async def rps(inter: Interaction, choice):  # NOTICE: The param which defines the option must have the exact same name.
    choices = ('rock', 'paper', 'scissors')  # We define a variable which holds a tuple with all the possible choices.
    bot_choice = random.choice(choices)  # We get the bot to pick a random value from ``choices``
    # This is not necessary, but here we define the lost message so we don't have to repeat ourselves each time the user loses
    lost_message = f'You lost. The bot chose **{bot_choice}** while you chose **{choice}**'
    # We do the same with the won message
    won_message = f'You won. You chose **{choice}** while the bot chose **{bot_choice}**'

    if choice == bot_choice:  # Check if the choice that the user picked is equal with the choice the bot picked.
        await inter.response.send_message(f'Draw. Both you and the bot chose: {choice}', ephemeral=True)

    # First we check if the user lost.
    if (
        (choice == 'rock' and bot_choice == 'paper') or 
        (choice == 'paper' and bot_choice == 'scissors') or 
        (choice == 'scissors' and bot_choice == 'rock')
    ):
        content = f'You lost. The bot chose **{bot_choice}** while you chose **{choice}**'
    elif choice == bot_choice:
        content = f'Draw. Both you and the bot chose: {choice}'
    else:
        content = f'You won. You chose **{choice}** while the bot chose **{bot_choice}**'
    
    await inter.response.send_message(content, ephemeral=True)

# Now we run the bot, and there you have it.
bot.run('token')