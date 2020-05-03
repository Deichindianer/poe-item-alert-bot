import logging

import boto3
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_ladder(ladder_name, ladder_limit):
    ssm = boto3.client("ssm")
    base_url = "http://api.pathofexile.com"
    url_path = f"ladders/{ladder_name}"
    ladder_url = f"{base_url}/{url_path}?limit={ladder_limit}"
    ladder = requests.get(ladder_url)
    headers = ladder.headers
    logger.debug(f"Resonse headers: {headers}")
    ladder_json = ladder.json()
    ssm.put_parameter(
        Name="/poe-api-exporter/ladder-cache-timestamp",
        Value=ladder_json["cached_since"],
        Type="String",
        Overwrite=True,
    )
    return ladder_json


def get_character(account_name, character_name):
    logger.debug(f"Getting {character_name} from account: {account_name}")
    base_url = "http://www.pathofexile.com"
    url_path = f"character-window/get-items"
    url_options = f"character={character_name}&accountName={account_name}"
    character_url = f"{base_url}/{url_path}?{url_options}"
    headers = {"content-type": "application/json"}
    # TODO: implement rate limiting logic because FUCK ME ITS PAINFUL
    character = requests.get(character_url, headers=headers)
    # {'error': {'code': 6, 'message': 'Forbidden'}}
    character_json = character.json()
    if character_json.get("error"):
        error = character_json["error"]
        if error["code"] == 1:
            logger.info(f"Character({character_name}) was deleted, skipping!")
        if error["code"] == 6:
            logger.info(f"Profile({account_name}) set to private, skipping!")
        else:
            logger.warning(f"Encountered error while running {account_name}: {error}")
        return {}
    # TODO: parse this json thing somehow LOL
    return character_json
