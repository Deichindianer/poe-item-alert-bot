import logging

import boto3
from boto3.dynamodb.types import TypeDeserializer

from items import ItemFilter


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def handler(event, context):
    ddb = boto3.client("dynamodb")
    all_characters = ddb.scan(
        TableName="poe_api_export_cache"
        # Key={"player_name": {"S": event["player_name"].lower()}}
    )
    logger.debug(f"Result: {all_characters}")
    result = []
    for character in all_characters["Items"]:
        deserializer = TypeDeserializer()
        parsed_char = {k: deserializer.deserialize(v) for k, v in character.items()}
        logger.debug(f"Character was parsed succesfully!")
        items = ItemFilter(parsed_char["player_data"]["items"], event["filter"])
        logger.info(f"Item filter applied successfully: {items.result}")
        result.append(
            {"player_name": parsed_char["player_name"], "items": items.result}
        )
    return result

    # if character.get("Items"):
    #     for item in character["Items"]:
    #     return {"Result": items.result}
    # else:
    #     logger.debug(f"Response: {character}")
    #     return {"Error": {"Message": "Character not in cache lol"}}
