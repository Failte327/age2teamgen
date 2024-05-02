# THIS FILE IS DEPRECATED, FUNCTIONALITY HAS BEEN MOVED INTO INTERFACE.PY

import requests
from bs4 import BeautifulSoup

user_id = 4289859
url = f"https://www.aoe2insights.com/user/{user_id}/matches/?ladder=0&player=&map=&played_civilization=&opponent_civilization=&duration=&position="

response = requests.get(url)
raw_data = response.text

parsed_data = BeautifulSoup(raw_data, features="lxml")

players = []
player_ratings = {}

links = parsed_data.select(".team-player")
for link in links:
    if link.find("a") is not None:
        link_string = link.find("a").string.strip()
        if link_string not in players:
            players.append(link_string)
        

for player in players:
    for link in links:
        if link.find("a") is not None:
            link_string = link.find("a").string.strip()
            if link_string == player:
                if len(link.parent.select(".rating > span")) > 0:
                    rating = link.parent.select(".rating > span")[0].string
                    if player not in player_ratings:
                        player_ratings[player] = rating

print(player_ratings)

