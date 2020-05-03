import logging
import time

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
    _rate_limit_backoff(headers)
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
    logger.debug(f"Response headers: {character.headers}")
    resp_headers = character.headers
    _rate_limit_backoff(resp_headers)
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


def _rate_limit_backoff(headers):
    current_rate_status = headers["X-Rate-Limit-Ip-State"].split(",")
    rate_rules = headers["X-Rate-Limit-Ip"].split(",")
    for status, rule in zip(current_rate_status, rate_rules):
        c_rate, c_int, c_pen = status.split(":")
        m_rate, m_int, m_pen = rule.split(":")
        logger.debug(f"Current rate: {c_rate}, {c_int}, {c_pen}")
        logger.debug(f"Max rate: {m_rate}, {m_int}, {m_pen}")
        rate_ratio = int(c_rate) / int(m_rate)
        if rate_ratio > 0.9:
            backoff_duration = int(m_int) * 0.25
            logger.warning(f"Rate is exceeding 90% backing off for {backoff_duration}s")
            time.sleep(backoff_duration)
