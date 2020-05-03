import json
import logging

# import datetime

from decimal import Decimal

import boto3

from poe_api_exporter import get_ladder, get_character
from util import remove_empty_string

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def handler(event, context):
    ssm = boto3.client("ssm")
    # this will break if the parameter doesn't exist :)
    ladder_cache_time = ssm.get_parameter(
        Name="/poe-api-exporter/ladder-cache-timestamp"
    )["Parameter"]["Value"]
    league = ssm.get_parameter(Name="/poe-item-alert/league")["Parameter"]["Value"]
    logger.debug(f"Got ladder cache time: {ladder_cache_time}")
    # utc_now = datetime.datetime.utcnow()
    # can't fuck with that now - no time
    # ladder_cache_time = datetime.strptime(
    #     ladder_cache_time["Parameter"]["Value"],
    #     "%y-%m-%dT%H%M%S%z"
    # )
    ladder = get_ladder(league, 10)
    ddb = boto3.resource("dynamodb")
    logger.debug(f"Matching {ladder_cache_time} with {ladder['cached_since']}")
    if ladder_cache_time == ladder["cached_since"]:
        logger.info(f"Cache has not updated yet skipping character insertion")
        return
    for player in ladder["entries"]:
        # filter out all mules to increase performance for the method rush event
        if player["character"]["class"] == "Scion":
            return
        account_name = player["account"]["name"]
        character_name = player["character"]["name"]
        character = get_character(account_name, character_name)
        if not character:
            logger.debug(f"Character encountered an error skipping.")
            continue
        # this log line will be spammy as fuck and huge
        # TODO: maybe get this table name from ssm parameter store later
        poe_api_cache_table = ddb.Table("poe_api_export_cache")
        # Kill me
        parsed_char = json.loads(json.dumps(character), parse_float=Decimal)
        ddb_item = remove_empty_string(parsed_char)
        poe_api_cache_table.put_item(
            Item={
                # TODO: not sure if this is player or account I'm loosing my mind
                "player_name": player["account"]["name"].lower(),
                "player_data": ddb_item,
            }
        )
