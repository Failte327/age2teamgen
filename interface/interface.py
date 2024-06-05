from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import random
import math

app = Flask(__name__)

@app.route('/')
def render_homepage():
    return render_template("base.html")

@app.route('/generate_teams',  methods=['POST'])
def team_generator():
    player_list = request.form.get("playername").split(",")
    print(player_list)

    user_id = 4289859 # Sean's user id, he's in most games so he's the easiest one to query
    url = f"https://www.aoe2insights.com/user/{user_id}/matches/?ladder=0&player=&map=&played_civilization=&opponent_civilization=&duration=&position="

    response = requests.get(url)
    raw_data = response.text

    parsed_data = BeautifulSoup(raw_data, features="lxml")

    players = []
    active_players = {}
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

    for i in player_list:
        print(i)
        for key, value in player_ratings.items():
            if i == key:
                active_players[key] = value

    team_count = (len(active_players)) / 2

    teams_set = False

    while teams_set is False:
        players_on_team_1 = {}
        players_on_team_2 = {}
        while len(players_on_team_1) < team_count:
            player = random.choice(list(active_players.items()))
            players_on_team_1[player[0]] = player[1]
        while len(players_on_team_2) < team_count:
            player = random.choice(list(active_players.items()))
            if player[0] not in players_on_team_1.keys():
                players_on_team_2[player[0]] = player[1]
        print(players_on_team_1)
        print(players_on_team_2)
        team_1_score = 0
        team_2_score = 0
        for i in players_on_team_1.values():
            team_1_score = (team_1_score + int(i)) / team_count
        for i in players_on_team_2.values():
            team_2_score = (team_2_score + int(i)) / team_count
        print(team_1_score)
        print(team_2_score)
        difference = team_1_score - team_2_score
        print(difference)
        if difference > 0:
            if difference <= 10:
                teams_set = True
        elif difference < 0:
            if difference >= -10:
                teams_set = True
    
    return {"Team_1": players_on_team_1, "Team_2": players_on_team_2}

## run cmd: flask --app interface run
