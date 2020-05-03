import asyncio
import logging
import os

import aiohttp

from poe.character import Character

logger = logging.getLogger("poe_alert_bot.ladder")


class Ladder:
    def __init__(self, name):
        self.name = name
        self.cookies = {"POESESSID": os.environ.get("POE_SESS_ID")}
        if not self.cookies:
            raise ValueError("You need to supply the environment var POE_SESS_ID")
        base_url = "http://api.pathofexile.com"
        url_path = f"ladders/{name}"
        if os.environ.get("LADDER_LIMIT"):
            ladder_limit = os.environ["LADDER_LIMIT"]
        else:
            ladder_limit = 50
        url_options = f"limit={ladder_limit}"
        self.url = f"{base_url}/{url_path}?{url_options}"

    async def _get_characters(self):
        headers = {"content-type": "application/json"}
        async with aiohttp.ClientSession(
            cookies=self.cookies, headers=headers
        ) as session:
            async with session.get(self.url) as r:
                ladder = await r.json()
                characters = ladder["entries"]
                return characters

    async def filter_all(self, filters):
        players = await self._get_characters()
        # characters = []
        for player in players:
            if player["character"]["class"] == "Scion":
                pass
            account_name = player["account"]["name"]
            character_name = player["character"]["name"]
            if player["account"].get("twitch"):
                twitch = player["account"]["twitch"]["name"]
            else:
                twitch = None
            # characters.append({"account": account_name, "char": character_name})
            character = Character(character_name, account_name, filters)
            items = await character.items()
            yield {"Player": account_name, "Twitch": twitch, "Items": items}
            await asyncio.sleep(0.5)
