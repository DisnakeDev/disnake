import disnake
from disnake.ext import commands
import asyncio
import secrets

bot = commands.Bot(command_prefix="-")

# Here we create a simple sequence of messages for the following command.

SEQUENCE = [
    """‎‎‎‎‎‎‎‏‏‎  ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‏‏‎‏🚀
Rocket launch starting in 0.""",
    """‏‏‎   ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‏🚀
\nRocket launch starting in 0.""",
    """‏‏‎ ‏‏‎ ‎‏‏‎ ‎‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‏‏‎🚀
    \n
Rocket launch starting in 0.
    """,
]


# For this example to how to use min and max value in slash commands,
# we are going to do a rocket launch.


@bot.slash_command(name="rocket-launch", description="Launch a rocket!")
async def rocket_launch(
    interaction: disnake.ApplicationCommandInteraction,
    seconds: int = commands.Param(min_value=5, max_value=15, description="Seconds to countdown."),
):

    # In this case, we will use min/max value for the seconds to count before the launch.

    await interaction.response.send_message(f"Rocket launch starting in {seconds}.")
    await asyncio.sleep(1)

    # Here we will do a countdown with the seconds input that the user gave.
    for i in range(1, seconds + 1):

        await interaction.edit_original_message(content=f"Rocket launch starting in {seconds - i}.")
        await asyncio.sleep(1)

    # Here we send the sequence of messages for the rocket launch,
    # we will edit the message in order to send the sequence.
    for sequencee in SEQUENCE:
        await interaction.edit_original_message(content=sequencee)
        await asyncio.sleep(1)

    # Here we will choice between "success" and "explosion",
    # in order to know if the rocket launch was success or not.
    rocket = secrets.choice(["success", "explosion"])

    if rocket == "success":
        # If the rocket launch was a success,
        # we will edit the message and send that it was success.
        success = [
            """‏‏‎‏‏‎‏‏‎ ‏‏‎ ‎‏‏‎ ‎‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‏‏‎🚀
            \n\nRocket launched successfully!
            """
        ]

        await interaction.edit_original_message(content=success[0])
    else:
        # If the rocket launch wasn't a success and it exploded,
        #  we will edit the message and send that it exploded.
        explosion = [
            """‏‏‎‏‏‎‏‏‎‏‏‎‏‏‎ ‏‏‎ ‎‏‏‎ ‎‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‏‏‎💥
            \n\nOh no, the rocket exploded.
            """
        ]

        await interaction.edit_original_message(content=explosion[0])


bot.run("token")
