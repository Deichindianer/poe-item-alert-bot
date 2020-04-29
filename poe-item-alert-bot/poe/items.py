class ItemFilter:
    def __init__(self, items, filters):
        self.items = items
        self.filters = filters
        self.result = self.filter()

    def filter(self):
        items = []
        for item in self.items:
            for i_filter in self.filters:
                if i_filter["filter_type"] == "type":
                    i_type = self._get_item_type(item)
                    if i_filter["filter_value"] in i_type:
                        items.append(item["typeLine"])
                elif i_filter["filter_type"] == "mod":
                    i_mods = self._get_item_mods(item)
                    for mod in i_mods:
                        if i_filter["filter_value"] in mod:
                            items.append(f"{item['typeLine']}({mod})")
                elif i_filter["filter_type"] == "type+mod":
                    f_type = i_filter["filter_value"].split("+")[0]
                    if f_type in self._get_item_type(item):
                        f_mod = i_filter["filter_value"].split("+")[1]
                        for mod in self._get_item_mods(item):
                            if f_mod in mod:
                                items.append(f"{item['typeLine']}({mod})")

        return items

    def _get_item_mods(self, item):
        try:
            return item["explicitMods"]
        except KeyError:
            return []

    def _get_item_type(self, item):
        return item["inventoryId"]
