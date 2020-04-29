import os

import aiohttp

from poe.items import ItemFilter


class Character:
    def __init__(self, name, account, filters):
        self.name = name
        self.account = account
        self.filters = filters
        base_url = "http://www.pathofexile.com"
        url_path = f"character-window/get-items"
        url_options = f"character={self.name}&accountName={account}"
        self.url = f"{base_url}/{url_path}?{url_options}"
        self.cookies = {"POESESSID": os.environ.get("POE_SESS_ID")}
        if not self.cookies:
            raise ValueError("You need to supply the environment var POE_SESS_ID")

    async def _get_char(self):
        headers = {"content-type": "application/json"}
        async with aiohttp.ClientSession(
            cookies=self.cookies, headers=headers
        ) as session:
            async with session.get(self.url) as r:
                character = await r.json()
                return character

    async def items(self):
        char = await self._get_char()
        if char.get("items"):
            items = char["items"]
            return ItemFilter(items, self.filters).result
        else:
            print(f"No items found for {char}")
            return []
