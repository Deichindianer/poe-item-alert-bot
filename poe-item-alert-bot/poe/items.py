class ItemFilter:
    def __init__(self, items, item_type):
        if item_type:
            self.items = [i["typeLine"] for i in items if i["typeLine"] == item_type]
        else:
            self.items = [i["typeLine"] for i in items]
