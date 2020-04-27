import asyncio
import os
import json

import aiohttp

from poe.async_char import Character

class Ladder():

    def __init__(self, name):
        self.name = name
        self.cookies = {"POESESSID": os.environ.get("POE_SESS_ID")}
        if not self.cookies:
            raise ValueError("You need to supply the environment var POE_SESS_ID")
        base_url = "http://api.pathofexile.com"
        url_path = f"ladders/{name}"
        url_options = "limit=200"
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
    
    async def filter_all(self, item_type):
        players = await self._get_characters()
        for player in players:
            account_name = player["account"]["name"]
            character_name = player["character"]["name"]
            character = Character(character_name, account_name, item_type)
            items = await character.items()
            yield {"Player": account_name, "Items": items}
            await asyncio.sleep(0.5)
        
