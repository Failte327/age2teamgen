from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import random
from loguru import logger

app = Flask(__name__)

players_to_ids = {"sjhalbleib": 4289859, "reklewt": 5375940, "smhalbleib": 6877853, "nomrom": 2804382, "djhalbleib": 6867836, "scotthalb": 6867861, "charletttehalbleib": 10061690, "iceyman8": 8230988, "country_slicker": 10785824, "kolob_eagle25": 6888316, "quintonius": 2182022, "meghalb": 7451904, "brando": 7436245, "brandonnelson68": 7436245, "stealy5": 6901071, "azorr": 10455474, "acbishop": 4527003, "father.th2": 1198985, "iceyman8": 8230988}


@app.route('/')
def render_homepage():
    return render_template("base.html")

@app.route('/map')
def choose_map():
    maps = ["Acclivity", "Acropolis", "African Clearing", "Aftermath", "Alpine Lakes", "Amazon Tunnel", "Arabia", "Archipelago", "Arena", "Atacama", "Baltic", "Black Forest", "Bog Islands", "Bogland", "Budapest", "Cenotes", "City of Lakes", "Coastal", "Coastal Forest", "Continental", "Crater", "Crater Lake", "Crossroads", "Enclosed", "Eruption", "Fortress", "Four Lakes", "Frigid Lake", "Ghost Lake", "Gold Rush", "Golden Pit", "Golden Swamp", "Greenland", "Haboob", "Hamburger", "Hideout", "Highland", "Hill Fort", "Islands", "Kawasan", "Kilimanjaro", "Land Madness", "Land Nomad", "Lombardia", "Lowland", "Mangrove Jungle", "Marketplace", "Meadow", "Mediterranean", "MegaRandom", "Michi", "Migration", "Mongolia", "Morass", "Mountain Pass", "Mountain Range", "Mountain Ridge", "Nile Delta", "Nomad", "Northern Isles", "Oasis", "Pacific", "Islands", "Ravines", "Ring Fortress", "Rivers", "Runestones", "Sacred Springs", "Salt Marsh", "Sandbank", "Scandinavia", "Seize The Mountain", "Serengeti", "Shoals", "Socotra", "Steppe", "Team Islands", "Team Moats", "Valley", "Volcanic Island", "Wade", "Water", "Nomad", "Wolf Hill", "Yucatan"]
    map_choice = random.choice(maps)
    logger.success("Generated random map: ", map_choice)
    return map_choice

@app.route('/generate_teams',  methods=['POST'])
def team_generator():
    # Construct player list from form
    player_list = request.form.get("playername").split(",")
    counter = 0
    for i in player_list:
        new = i.strip().lower()
        player_list[counter] = new
        counter = counter + 1
        if i not in players_to_ids.keys():
            return f"Playername {i} not found in list of known players."


    currently_playing = {}
    player_ratings = {}

    for player, id in players_to_ids.items():
        if player in player_list:
            currently_playing[player] = id

    logger.debug("Querying aoe2insights.com for player ratings...")
    for name, user_id in currently_playing.items():
        url = f"https://www.aoe2insights.com/user/{user_id}/matches/?ladder=0&player=&map=&played_civilization=&opponent_civilization=&duration=&position="
        response = requests.get(url)
        raw_data = response.text
        parsed_data = BeautifulSoup(raw_data, features="lxml")

        # Construct data objects linking players to their ratings
        links = parsed_data.select(".team-player")
        for link in links:
            if link.find("a") is not None:
                link_string = link.find("a").string.strip().lower()
                if link_string == name:
                    if len(link.parent.select(".rating > span")) > 0:
                        rating = link.parent.select(".rating > span")[0].string
                        if name not in player_ratings.keys():
                            player_ratings[name] = rating
        if name == "meghalb":
            player_ratings[name] = 800
        elif name == "Brando":
            player_ratings[name] = 700
        elif name == "teancum00":
            player_ratings[name] = 800

    logger.success("Ratings from aoe2insights acquired")
    logger.debug(f"aoe2insights Ratings: {player_ratings}")

    # Create random player combinations until we have a difference in rating below the acceptable threshold
    team_count = (len(currently_playing)) / 2
    logger.debug(f"Players per team: {team_count}",)
    teams_set = False
    tries = 0

    logger.debug("Generating Teams...")
    while teams_set is False:
        players_on_team_1 = {}
        players_on_team_2 = {}
        while len(players_on_team_1) < team_count:
            player = random.choice(list(player_ratings.items()))
            players_on_team_1[player[0]] = player[1]
        while len(players_on_team_2) < team_count:
            player = random.choice(list(player_ratings.items()))
            if player[0] not in players_on_team_1.keys():
                players_on_team_2[player[0]] = player[1]
        logger.info(f"Team 1 Candidate: {players_on_team_1}")
        logger.info(f"Team 2 Candidate: {players_on_team_2}")
        team_1_score = 0
        team_2_score = 0
        for i in players_on_team_1.values():
            team_1_score = (team_1_score + int(i)) / team_count
        for i in players_on_team_2.values():
            team_2_score = (team_2_score + int(i)) / team_count
        logger.debug(f"Team 1 Candidate Aggregate Rating: {team_1_score}")
        logger.debug(f"Team 2 Candidate Aggregate Rating: {team_2_score}")
        difference = team_1_score - team_2_score

        logger.info(f"Team Score Difference: {difference}")
        tries = tries + 1
        logger.debug(f"Attempts at matching teams: {tries}")
        if tries <= 15:
            if difference > 0:
                if difference <= 5:
                    teams_set = True
            elif difference < 0:
                if difference >= -5:
                    teams_set = True
        elif tries > 15 and tries <= 30:
            if difference > 0:
                if difference <= 10:
                    teams_set = True
            elif difference < 0:
                if difference >= -10:
                    teams_set = True
        elif tries > 30 and tries <= 100:
            if difference > 0:
                if difference <= 20:
                    teams_set = True
            elif difference < 0:
                if difference >= -20:
                    teams_set = True
        elif tries > 100:
            teams_set = True

        if teams_set == False:
            logger.error("Rating difference not within desired parameters, generating again...")
    teams = {"Team_1": list(players_on_team_1.keys()), "Team_2": list(players_on_team_2.keys())}
    logger.success(f"Teams generated: {teams}")
    return teams

@app.route('/stats')
def get_stats():
    data = request.args.get("user")

    for key, value in players_to_ids.items():
        if key == data:
            url = f"https://www.aoe2insights.com/user/{value}/stats/0/frequent-opponents"
            response = requests.get(url)
            raw_data = response.text
            parsed_data = BeautifulSoup(raw_data, features="lxml")
            table = parsed_data.select("table")
            for el in table:
                for i in el.select("a", href=True):
                    partial = i["href"]
                    i["href"] = f"https://www.aoe2insights.com{partial}"
            stats = str(table).strip('[]')
            url2 = f"https://www.aoe2insights.com/user/{value}/stats/0/frequent-teammates"
            response2 = requests.get(url2)
            raw_data2 = response2.text
            parsed_data2 = BeautifulSoup(raw_data2, features="lxml")
            table2 = parsed_data2.select("table")
            stats = stats + (str(table2).strip("[]"))
            return stats

## dev run cmd: flask --app interface run -p10000
## prod run cmd ?
