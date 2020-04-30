import logging

import aiohttp

from poe.items import ItemFilter

logger = logging.getLogger("poe_alert_bot.character")


class Character:
    def __init__(self, name, account, item_filters):
        logger.info(f"Initialized character {name}!")
        self.name = name
        self.account = account
        self.item_filters = item_filters
        base_url = "http://www.pathofexile.com"
        url_path = f"character-window/get-items"
        url_options = f"character={self.name}&accountName={account}"
        self.url = f"{base_url}/{url_path}?{url_options}"

    async def _get_char(self):
        logger.debug(f"Requesting character data from poe api...")
        headers = {"content-type": "application/json"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(self.url) as r:
                character = await r.json()
                if character.get("error"):
                    return {"character": {"name": f"{self.name}"}}
                return character

    async def items(self):
        char = await self._get_char()
        # logger.debug(char)
        if char.get("items"):
            logger.debug("Character has items!")
            items = char["items"]
            filtered_items = {}
            for item_filter in self.item_filters:
                logger.debug(f"Running {item_filter} over items...")
                item_filter_msg = (
                    f"{item_filter['filter_type']} {item_filter['filter_value']}"
                )
                filtered_items[item_filter_msg] = ItemFilter(items, item_filter).result
            filtered_vals = [i for i in filtered_items.values()]
            logger.debug(f"Result of the filter: {filtered_vals}")
            if any(filtered_vals):
                logger.info(f"Found {filtered_items}")
                return filtered_items
            else:
                return []
        else:
            logger.info(f"No items found for {char['character']['name']}")
            return []
