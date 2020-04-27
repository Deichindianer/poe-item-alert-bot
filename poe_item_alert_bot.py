import os
import time
import json

import requests

def send_discord_message(channel, token, content):
    url = f"https://discordapp.com/api/v6/channels/{channel}/messages"
    headers = {
        "Authorization": f"Bot {token}",
        "content-type": "application/json"
    }
    body = {"content": f"{content}", "tts": False}
    response = requests.post(url, headers=headers, json=body)
    return response


def get_ladder(league):
    ladder = requests.get(league).json()
    return ladder["entries"]


def get_character(character, account, poe_sess_id):
    url = f"http://www.pathofexile.com/character-window/get-items?character={character}&accountName={account}"
    cookies = {"POESESSID": poe_sess_id}
    character = requests.get(url, cookies=cookies).json()
    # print(json.dumps(character["items"], indent=4))
    try:
        items = [i for i in character["items"] if i["inventoryId"] != "Flask"]
        flasks = [i["typeLine"] for i in character["items"] if i["inventoryId"] == "Flask"]
    except KeyError:
        return [], []
    return items, flasks


def filter_items(items):
    response = []
    for i in items:
        if i["inventoryId"] == "Boots":
            try:
                for mod in i["explicitMods"]:
                    if "Movement Speed" in mod:
                        speed = mod.split(" ")[0]
                        response.append(f"{speed} movement speed boots!")
            except KeyError:
                # just white item so skipping
                pass
    return response
                

def filter_flasks(flasks):
    response = []
    for f in flasks:
        if "Adrenaline" in f:
            response.append(f)
        elif "Panicked" in f:
            response.append(f)
        elif "Seething" in f:
            response.append(f)
    return response


def main():
    discord_channel = os.environ["DISCORD_CHANNEL"]
    discord_token = os.environ["DISCORD_TOKEN"]
    poe_sess_id = os.environ["POE_SESS_ID"]
    character = os.environ["POE_CHAR"]
    account = os.environ["POE_ACCOUNT"]
    ladder = get_ladder("http://api.pathofexile.com/ladders/Method Rush Kitava Race Four (PL8876)?limit=200")
    for player in ladder:
        char_name = player["character"]["name"]
        account_name = player["account"]["name"]
        print(char_name)
        items, flasks = get_character(char_name, account_name, poe_sess_id)
        print(json.dumps(items, indent=4))
        flask_alert = filter_flasks(flasks)
        item_alert = filter_items(items)
        content = ""
        # if item_alert:
        #     content = f"{char_name}\n```{item_alert}```"
        # if flask_alert:
        #     content += f"{char_name}\n```{flask_alert}```"
        #     print(send_discord_message(discord_channel, discord_token, content))
        # content = f"""__*{char_name}*__
        # Items:\n{items}
        # Flasks:\n{flasks}
        # """
        time.sleep(2)

if __name__ == "__main__":
    main()
