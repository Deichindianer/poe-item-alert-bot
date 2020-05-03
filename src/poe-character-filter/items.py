import logging

logger = logging.getLogger("poe_alert_bot.items")


class ItemFilter:
    def __init__(self, items, item_filter):
        logger.info(f"Initialized ItemFilter with {item_filter}")
        self.items = items
        self.item_filter = item_filter
        self.result = self.filter()

    def filter(self):
        items = []
        for item in self.items:
            logger.debug(f"{item['typeLine']} being evaluated...")
            result = []
            filter_types = self.item_filter["filter_type"].split("+")
            filter_values = self.item_filter["filter_value"].split("+")
            logger.debug(f"Found filter types: {filter_types}")
            logger.debug(f"Found filter values: {filter_values}")
            for f_type, f_value in zip(filter_types, filter_values):
                mod = None
                links = None
                unique_name = None
                if f_type == "type":
                    logger.debug(f"Running a type filter on {item['typeLine']}")
                    filter_result = self.type_filter(item, f_value)
                    logger.debug(f"{item['typeLine']} - {filter_result}")
                    result.append(filter_result)
                elif f_type == "mod":
                    # logger.debug(f"Running a mod filter on {item['typeLine']}")
                    filter_result, mod = self.mod_filter(item, f_value)
                    logger.debug(f"{item['typeLine']} - {filter_result}")
                    result.append(filter_result)
                elif f_type == "links":
                    # logger.debug(f"Running a link filter on {item['typeLine']}")
                    filter_result, links = self.link_filter(item, f_value)
                    result.append(filter_result)
                elif f_type == "unique":
                    # logger.debug(f"Running a link filter on {item['typeLine']}")
                    filter_result, unique_name = self.unique_filter(item, f_value)
                    result.append(filter_result)
                else:
                    ValueError("Bad filter type supplied! Oh no!")
            if result:
                # all() would make an empty list appear as True
                if all(result):
                    logger.debug(f"Result of all filters: {result}")
                    # order matters here ugh
                    # I won't explode this out to match unique filters as well
                    # at least not until someone complains :D
                    if links and mod:
                        logger.debug(f"Mod and link filters matched!")
                        logger.debug(f"{item['typeLine']}({links}L)[{mod}]")
                        items.append(f"{item['typeLine']}({links}L)[{mod}]")
                    elif mod:
                        logger.debug(f"Mod filter matched")
                        logger.debug(f"{item['typeLine']}[{mod}]")
                        items.append(f"{item['typeLine']}[{mod}]")
                    elif links:
                        logger.debug(f"Link filter matched")
                        logger.debug(f"{item['typeLine']}({links}L)")
                        items.append(f"{item['typeLine']}({links}L)")
                    elif unique_name:
                        logger.debug(f"Unique filter matched")
                        logger.debug(f"{item['name']}")
                        items.append(f"{item['name']}")
                    else:
                        logger.debug(f"Type filter matched")
                        logger.debug(f"{item['typeLine']}")
                        items.append(f"{item['typeLine']}")
        logger.info(f"Matched items: {items}")
        return items

    def type_filter(self, item, filter_value):
        item_type = self._get_item_type(item)
        if filter_value in item_type:
            return True
        return False

    def mod_filter(self, item, filter_value):
        item_mods = self._get_item_mods(item)
        for mod in item_mods:
            logger.debug(f"Matching {mod} against {filter_value}")
            if filter_value in mod:
                logger.debug(f"Found match!")
                return True, mod
        return False, None

    def link_filter(self, item, filter_value):
        item_links = self._get_item_links(item)
        if item_links >= int(filter_value):
            return True, item_links
        return False, None

    def unique_filter(self, item, filter_value):
        if filter_value == "any":
            if item.get("flavourText"):
                return True, item["name"]
        else:
            if item.get("flavourText"):
                if item["name"] == filter_value:
                    return True, item["name"]
        return False, None

    def _get_item_mods(self, item):
        try:
            return item["explicitMods"]
        except KeyError:
            return []

    def _get_item_type(self, item):
        return item["inventoryId"]

    def _get_item_links(self, item):
        if item.get("sockets"):
            item_sockets = item["sockets"]
            link_count = 0
            for socket in item_sockets:
                logger.debug(f"Checking {socket}")
                if socket["group"] == 0:
                    logger.debug(f"Socket in group 0 found!")
                    link_count += 1
            logger.debug(f"Found links: {link_count}")
            return link_count
        else:
            return 0
