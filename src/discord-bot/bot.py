import logging
import os
import time
import json

import boto3

from discord import Embed
from discord.ext import commands


logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("poe_alert_bot")
if os.environ.get("LOG_LEVEL"):
    logger.setLevel(os.environ["LOG_LEVEL"])
else:
    logger.setLevel("INFO")

bot = commands.Bot(command_prefix="!item-alert-dev ")


@bot.command()
async def find(ctx, *args):
    logging.info(f"Got alert event: {args}")
    client = boto3.client("lambda", region_name="eu-central-1")
    start_time = time.perf_counter()
    # expect something like type:TypeName or mod:ModValue
    if args:
        filters = []
        for arg in args:
            filter_type = arg.split(":")[0]
            filter_value = arg.split(":")[1]
            filters.append({"filter_type": filter_type, "filter_value": filter_value})
        logger.debug(f"Created filter list: {filters}")
    for f in filters:
        title = f"{f['filter_type']} | {f['filter_value']}"
        message = Embed(title=title)
        payload = {
            "filter": {
                "filter_type": f["filter_type"],
                "filter_value": f["filter_value"],
            }
        }
        logger.debug(f"Invoking lambda for all characters with {payload}")
        resp = client.invoke(
            FunctionName="poe-character-filter",
            InvocationType="RequestResponse",
            Payload=json.dumps(payload),
        )
        result = json.loads(resp["Payload"].read().decode("utf-8"))
        logger.debug(f"Lambda ran successfully!")
        logger.debug(type(result))
        for player in result:
            if player["items"]:
                logger.debug(f"Adding {player['player_name']} to message...")
                message.add_field(
                    name=player["player_name"],
                    value=", ".join(player["items"]),
                    inline=True,
                )
            else:
                logger.debug(f"{player['player_name']} has no matching items.")
        stop_time = time.perf_counter()
        duration = f"{stop_time - start_time:0.2f}"
        message.add_field(name="Duration", value=f"{duration}s", inline=False)
        logger.debug(f"Sending message...")
        await ctx.send(embed=message)
        logger.debug(f"Ran query in {duration} seconds")


@bot.command()
async def set_league(ctx, league_name):
    client = boto3.client("ssm", region_name="eu-central-1")
    logger.debug(f"Got set_league event {ctx}")
    client.put_parameter(
        Name="/poe-item-alert/league", Value=league_name, Type="String", Overwrite=True
    )
    await ctx.send(f"Set active league: {league_name}")


@bot.command()
async def get_league(ctx):
    client = boto3.client("ssm", region_name="eu-central-1")
    logger.debug(f"Got get_league event {ctx}")
    resp = client.get_parameter(Name="/poe-item-alert/league")
    league = resp["Parameter"]["Value"]
    await ctx.send(f"Current active league: {league}")


bot.run(os.environ["DISCORD_TOKEN"])
