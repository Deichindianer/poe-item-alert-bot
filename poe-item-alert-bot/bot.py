import logging
import os
import time

from discord import Embed
from discord.ext import commands

from poe.ladder import Ladder
from util import match_player_to_acc

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("poe_alert_bot")
if os.environ.get("LOG_LEVEL"):
    logger.setLevel(os.environ["LOG_LEVEL"])
else:
    logger.setLevel("INFO")
tter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

bot = commands.Bot(command_prefix="!item-alert ")


@bot.command()
async def find(ctx, *args):
    logging.info(f"Got alert event: {args}")
    start_time = time.perf_counter()
    try:
        logger.info("Using existing league_cache to identify league")
        with open("/tmp/poe_item_alert_bot_league_cache") as f:
            ladder_cache = f.read()
        ladder = Ladder(ladder_cache)
        await ctx.send(f"Running search in {ladder_cache} for {args}")
    except FileNotFoundError:
        logger.warning("No league cache present needs to be created!")
        await ctx.send(
            "Please set the league with `!item-alert set_league league_name`"
        )
        return
    # expect something like type:TypeName or mod:ModValue
    if args:
        filters = []
        for arg in args:
            filter_type = arg.split(":")[0]
            filter_value = arg.split(":")[1]
            filters.append({"filter_type": filter_type, "filter_value": filter_value})
        logger.debug(f"Created filter list: {filters}")
    title = ""
    for f in filters:
        title += f"{f['filter_type']} | {f['filter_value']} -"
    title = title[:-2]
    message = Embed(title=title)
    async for player in ladder.filter_all(filters):
        logger.debug(f"Running through {player}")
        try:
            actual_name = match_player_to_acc(player["Player"].lower())
        except KeyError:
            actual_name = player["Player"]
        item_list = []
        for item in player["Items"]:
            if item:
                item_list.append(True)
            else:
                item_list.append(False)
        if any(item_list):
            logger.info(f"Found {player}")
            # if player["Twitch"]:
            #     twitch_link = f"https://twitch.tv/{player['Twitch']}"
            #     message = f"**{player['Player']}**({twitch_link}) has matching items:\n"
            # else:
            # title = f"{actual_name} has matching items"
            for item_filter, items in player["Items"].items():
                if items:
                    logger.debug(f"Adding message {actual_name}")
                    message.add_field(
                        name=actual_name, value=", ".join(items), inline=True
                    )
        else:
            logger.info(f"{player['Player']} does not match filter")
    stop_time = time.perf_counter()
    duration = f"{stop_time - start_time:0.2f}"
    message.add_field(name="Duration", value=f"{duration}s", inline=False)
    await ctx.send(embed=message)
    logger.debug(f"Ran query in {duration} seconds")


@bot.command()
async def set_league(ctx, league_name):
    with open("/tmp/poe_item_alert_bot_league_cache", "w+") as f:
        f.write(league_name)
    await ctx.send(f"Set active league: {league_name}")


@bot.command()
async def get_league(ctx):
    with open("/tmp/poe_item_alert_bot_league_cache") as f:
        league = f.read()
    await ctx.send(f"Current active league: {league}")


bot.run(os.environ["DISCORD_TOKEN"])
