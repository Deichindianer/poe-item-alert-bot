import json
import os

from discord.ext import commands

# from poe.character import Character
from poe.ladder import Ladder

bot = commands.Bot(command_prefix="$")


@bot.command()
async def alert(ctx, player, *args):
    if player == "all":
        ladder = Ladder(os.environ["POE_LADDER"])
        # expect something like type:TypeName or mod:ModValue
        if args:
            filters = []
            for arg in args:
                filter_type = arg.split(":")[0]
                filter_value = arg.split(":")[1]
                filters.append(
                    {"filter_type": filter_type, "filter_value": filter_value}
                )

        async for player in ladder.filter_all(filters):
            if player["Items"]:
                print(f"Found {player}")
                await ctx.send(json.dumps(player))
            else:
                print(f"{player['Player']} does not match filter")


bot.run(os.environ["DISCORD_TOKEN"])
