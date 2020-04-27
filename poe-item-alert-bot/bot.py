import json
import os
import time

import discord
from discord.ext import commands

from poe.async_char import Character
from poe.ladder import Ladder

bot = commands.Bot(command_prefix="$")

@bot.command()
async def alert(ctx, player, item_type=None):
    if player == "all":
        ladder = Ladder(os.environ["POE_LADDER"])
        async for player in ladder.filter_all(item_type):
            if player["Items"]:
                print(f"Found {player}")
                await ctx.send(json.dumps(player))
            else:
                print(f"{player['Player']} does not match filter")
    else:
        char_name = "HAVOAHVUHDUSIYGVSDYIGF"
        account_name = "sanguinespirit"
        character = Character(char_name, account_name)
        items = await character.items(item_type)
        await ctx.send(json.dumps(items, indent=4))

bot.run(os.environ["DISCORD_TOKEN"])
