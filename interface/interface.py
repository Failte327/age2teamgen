from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import random

app = Flask(__name__)

@app.route('/')
def render_homepage():
    return render_template("base.html")

@app.route('/map')
def choose_map():
    maps = ["Acclivity", "Acropolis", "African Clearing", "Aftermath", "Alpine Lakes", "Amazon Tunnel", "Arabia", "Archipelago", "Arena", "Atacama", "Baltic", "Black Forest", "Bog Islands", "Bogland", "Budapest", "Cenotes", "City of Lakes", "Coastal", "Coastal Forest", "Continental", "Crater", "Crater Lake", "Crossroads", "Enclosed", "Eruption", "Fortress", "Four Lakes", "Frigid Lake", "Ghost Lake", "Gold Rush", "Golden Pit", "Golden Swamp", "Greenland", "Haboob", "Hamburger", "Hideout", "Highland", "Hill Fort", "Islands", "Kawasan", "Kilimanjaro", "Land Madness", "Land Nomad", "Lombardia", "Lowland", "Mangrove Jungle", "Marketplace", "Meadow", "Mediterranean", "MegaRandom", "Michi", "Migration", "Mongolia", "Morass", "Mountain Pass", "Mountain Range", "Mountain Ridge", "Nile Delta", "Nomad", "Northern Isles", "Oasis", "Pacific", "Islands", "Ravines", "Ring Fortress", "Rivers", "Runestones", "Sacred Springs", "Salt Marsh", "Sandbank", "Scandinavia", "Seize The Mountain", "Serengeti", "Shoals", "Socotra", "Steppe", "Team Islands", "Team Moats", "Valley", "Volcanic Island", "Wade", "Water", "Nomad", "Wolf Hill", "Yucatan"]
    map_choice = random.choice(maps)
    print(map_choice)
    return map_choice

@app.route('/generate_teams',  methods=['POST'])
def team_generator():
    # Strip whitespace
    player_list = request.form.get("playername").split(",")
    counter = 0
    for i in player_list:
        new = i.strip().lower()
        player_list[counter] = new
        counter = counter + 1

    print(player_list)

    # Get stats from aoe2insights.com
    user_id = 4289859 # Sean's user id, he's in most games so he's the easiest one to query
    url = f"https://www.aoe2insights.com/user/{user_id}/matches/?ladder=0&player=&map=&played_civilization=&opponent_civilization=&duration=&position="
    response = requests.get(url)
    raw_data = response.text
    parsed_data = BeautifulSoup(raw_data, features="lxml")

    # Construct data objects linking players to their ratings
    players = []
    active_players = {}
    player_ratings = {}
    links = parsed_data.select(".team-player")
    for link in links:
        if link.find("a") is not None:
            link_string = link.find("a").string.strip().lower()
            if link_string not in players:
                players.append(link_string)

    print(players)
    for player in players:
        for link in links:
            if link.find("a") is not None:
                link_string = link.find("a").string.strip().lower()
                if link_string == player:
                    if len(link.parent.select(".rating > span")) > 0:
                        rating = link.parent.select(".rating > span")[0].string
                        if player not in player_ratings:
                            player_ratings[player] = rating

    print(player_ratings)
    alternate_lookup_ids = [7436245, 2804382, 7451904, 10061690]
    for i in player_list:
        if i == "meghalb":
            active_players[i] = "800"
        elif i == "brandonnelson68":
            active_players[i] = "700"
        elif i == "teancum00":
            active_players[i] = "800"
        else:
            for key, value in player_ratings.items():
                if i == key:
                    active_players[key] = value
            # Get stats from other profile pages if we can't find the player
            if i not in player_ratings.keys():
                no_rating = True
                for n in alternate_lookup_ids:
                    user_id = n
                    url = f"https://www.aoe2insights.com/user/{user_id}/matches/?ladder=0&player=&map=&played_civilization=&opponent_civilization=&duration=&position="
                    response = requests.get(url)
                    raw_data = response.text
                    parsed_data = BeautifulSoup(raw_data, features="lxml")
                    links = parsed_data.select(".team-player")
                    for link in links:
                        if link.find("a") is not None:
                            link_string = link.find("a").string.strip().lower()
                            if link_string == i:
                                players.append(link_string)
                                if len(link.parent.select(".rating > span")) > 0:
                                    rating = link.parent.select(".rating > span")[0].string
                                    active_players[i] = rating
                                    no_rating = False
                # If we still can't find the player, return error
                if no_rating is True:
                    return "Error occurred, player is not in the list of known participants."



    # Create random player combinations until we have a difference in rating below the acceptable threshold
    team_count = (len(active_players)) / 2
    teams_set = False
    tries = 0

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
        tries = tries + 1
        print(f"Attempts at matching teams: {tries}")
        if tries <= 15:
            if difference > 0:
                if difference <= 10:
                    teams_set = True
            elif difference < 0:
                if difference >= -10:
                    teams_set = True
        elif tries > 15 and tries <= 30:
            if difference > 0:
                if difference <= 50:
                    teams_set = True
            elif difference < 0:
                if difference >= -50:
                    teams_set = True
        elif tries > 30 and tries <= 100:
            if difference > 0:
                if difference <= 100:
                    teams_set = True
            elif difference < 0:
                if difference >= -100:
                    teams_set = True
        elif tries > 100:
            teams_set = True
    
    teams = {"Team_1": list(players_on_team_1.keys()), "Team_2": list(players_on_team_2.keys())}
    return render_template("teams.html", teams=teams)

## run cmd: flask --app interface run
