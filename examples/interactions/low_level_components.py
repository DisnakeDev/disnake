"""
An example on how to send and process components without using views.
"""

import os

import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned)


# As an alternative to using views, it is possible to use a more low-level approach to components.
# Firstly, components do not have to be sent as part of a view. Instead, they can be sent as-is.
# Take special note of the fact that `custom_id`s have been explicitly set on these components.

# The main advantage of this is that listeners are, by nature, persistent.
# Each listener is stored on the bot strictly once, and are shared by all components.
# Because of this, their memory footprint will generally be smaller than that of an equivalent view.


@bot.command()
async def send_button(ctx: commands.Context):
    await ctx.send(
        "Here's a button!", components=disnake.ui.Button(label="Click me!", custom_id="cool_button")
    )


@bot.command()
async def send_select(ctx: commands.Context):
    await ctx.send(
        "Here's a select!",
        components=disnake.ui.Select(options=["1", "2", "3"], custom_id="cool_select")
        # Note: specifying select options in a list/dict requires disnake version 2.5.0 or newer.
    )


# To send multiple components, they can simply be stored in a list. They will then automatically
# fill out rows as they fit, similar to views if `row` is not set on the components. If a specific
# row ordering is desired, simply store them in a list of lists or `disnake.ui.ActionRow`s instead:


@bot.command()
async def send_all_the_buttons(ctx: commands.Context):
    buttons = []
    for y in range(4):
        buttons.append(row := disnake.ui.ActionRow())
        for x in range(4):
            row.add_button(label=f"({x}, {y})", custom_id=f"gridbutton_{x}_{y}")

    await ctx.send("Here's a 4x4 grid of buttons:", components=buttons)


# As-is, the components sent by these commands will do absolutely nothing. To remedy this, you
# would use a listener. Think of the listener as an equivalent to a view button's callback.
# However, the listener would function as a callback for **all** buttons. This is where the
# `custom_id` comes in: by filtering for the correct custom_id, a listener can be made to respond
# to a specific range of components.


# In this case, listening for only buttons is sufficient, thus the `on_button_click`-event is used.
# The equivalent event for select menus is `on_dropdown`. For modals, this is `on_modal_submit`.
# Finally, for _any_ kind of message interaction, the relevant event is `on_message_interaction`.


@bot.listen("on_button_click")
async def cool_button_listener(inter: disnake.MessageInteraction):
    if inter.component.custom_id != "cool_button":
        # This is used to filter interactions for components other than the button we wish to
        # process with this listener. Since `inter.component` returns the component that triggered
        # the interaction, in this case the button that was pressed, by means of comparison we can
        # filter any other button presses out.
        return

    # And thus, we end up with only buttons sent by command `send_button`.
    # At this point, this listener is practically identical to the callback of a view button.
    await inter.response.send_message("You clicked the cool button!")


# Similarly, a listener for the select can be created:


@bot.listen("on_dropdown")
async def cool_select_listener(inter: disnake.MessageInteraction):
    if inter.component.custom_id != "cool_select":
        # The same principle as for the button, any selects with the wrong `custom_id` are ignored.
        return

    # At this point, this listener is practically identical to the callback of a view select.
    await inter.response.send_message(f"You selected {inter.values}!")


# Lastly, a more generic type of listener for the example with multiple buttons:


@bot.listen("on_button_click")
async def grid_listener(inter: disnake.MessageInteraction):
    if not inter.component.custom_id or not inter.component.custom_id.startswith("gridbutton"):
        # The same principle again, except this time we want all buttons that start with grid_button,
        # as there are now 16 different `custom_id`s. This is a much better idea than making 16
        # different listeners, one for each button, of course!
        return

    # Now we can extract the x/y data...
    _, x, y = inter.component.custom_id.split("_")
    await inter.response.send_message(f"You hit ({x}, {y}). You sunk my battleship!")


# Since these `custom_id`s are stored on the buttons and the listeners aren't dependent on any kind
# of state, the components handled this way will remain fully functional over bot reloads!

# Note that listeners can also be added inside of cogs. For this, the only changes that would have
# to be made are to use `commands.Cog.listener` instead of `bot.listen`, and the first argument of
# the listener would have to be self.


bot.run(os.getenv("BOT_TOKEN"))
