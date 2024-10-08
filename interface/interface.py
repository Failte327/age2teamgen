from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import random
from sqlalchemy import create_engine, text
from loguru import logger

engine = create_engine("sqlite:///players.db")

app = Flask(__name__)

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
    
    players_to_ids = {}
    players_to_custom_ratings = {}

    # Get known player ids from the database
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM players;"))
        for row in result:
            for i in player_list:
                if row.player_name.lower() == i:
                    players_to_ids[i] = row.aoe2_insights_id
                    players_to_custom_ratings[i] = row.rating
    
    player_ratings = {}

    logger.success("Ratings from in-house database acquired")
    logger.debug(f"Database Ratings: {players_to_custom_ratings}")

    logger.debug("Querying aoe2insights.com for player ratings...")
    for name, user_id in players_to_ids.items():
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
        elif name == "brandonnelson68":
            player_ratings[name] = 700
        elif name == "teancum00":
            player_ratings[name] = 800

    logger.success("Ratings from aoe2insights acquired")
    logger.debug(f"aoe2insights Ratings: {player_ratings}")

    # Create random player combinations until we have a difference in rating below the acceptable threshold
    team_count = (len(players_to_ids)) / 2
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
    known_ids = {}
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM players;"))
        for row in result:
            known_ids[row.player_name] = row.aoe2_insights_id

    for key, value in known_ids.items():
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
        
@app.route('/add_player', methods=["POST"])
def add_player():
    player_name = request.form.get("new_player_name")
    aoe2_insights_id = request.form.get("aoe2_insights_id")
    inhouse_rating = request.form.get("inhouse_rating")

    conn = engine.connect()
    conn.execute(text(f"INSERT INTO players (player_name, aoe2_insights_id, rating) VALUES ('{player_name}', {aoe2_insights_id}, {inhouse_rating});"))
    conn.commit()
    conn.close()
    logger.success(f"Player {player_name} with aoe2insights id {aoe2_insights_id} has been added to the database.")
    return f"{player_name} added to player database."
## run cmd: flask --app interface run -p10000
