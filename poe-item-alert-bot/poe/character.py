import os
import json

import requests


class Character():

    def __init__(self, name, account):
        self.name = name
        self.account = account
        base_url = "http://www.pathofexile.com"
        url_path = f"character-window/get-items"
        url_options = f"character={self.name}&accountName={account}"
        self.url = f"{base_url}/{url_path}?{url_options}"
        self.cookies = {"POESESSID": os.environ.get("POE_SESS_ID")}
        if not self.cookies:
            raise ValueError("You need to supply the environment var POE_SESS_ID")
        self.items = self._get_char()
    
    def  _get_char(self):
        headers = {"content-type": "application/json"}
        char = requests.get(
            self.url,
            cookies=self.cookies,
            headers=headers).json()
        return char["items"]

