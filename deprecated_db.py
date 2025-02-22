# Get known player ids from the database
# with engine.connect() as conn:
#     try:
#         result = conn.execute(text("SELECT * FROM players;"))
#         for row in result:
#             for i in player_list:
#                 if row.player_name.lower() == i:
#                     players_to_ids[i] = row.aoe2_insights_id
#                     players_to_custom_ratings[i] = row.rating
#     except:
#       ----- get from array here -----

# logger.success("Ratings from in-house database acquired")
# logger.debug(f"Database Ratings: {players_to_custom_ratings}")


# engine = create_engine("sqlite:///players.db")

#    data = request.args.get("user")
#   known_ids = {}
#   with engine.connect() as conn:
#     result = conn.execute(text("SELECT * FROM players;"))
#     for row in result:
#         known_ids[row.player_name] = row.aoe2_insights_id

# @app.route('/add_player', methods=["POST"])
# def add_player():
#     player_name = request.form.get("new_player_name")
#     aoe2_insights_id = request.form.get("aoe2_insights_id")
#     inhouse_rating = request.form.get("inhouse_rating")

#     conn = engine.connect()
#     conn.execute(text(f"INSERT INTO players (player_name, aoe2_insights_id, rating) VALUES ('{player_name}', {aoe2_insights_id}, {inhouse_rating});"))
#     conn.commit()
#     conn.close()
#     logger.success(f"Player {player_name} with aoe2insights id {aoe2_insights_id} has been added to the database.")
#     return f"{player_name} added to player database."

