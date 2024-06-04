from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def render_homepage():
    return render_template("base.html")

@app.route('/generate_teams',  methods=['POST'])
def team_generator():
    player_list = request.form.get("playername").split()
    print(player_list)

    user_id = 4289859 # Sean's user id, he's in most games so he's the easiest one to query
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
    return player_ratings

## run cmd: flask --app interface run
