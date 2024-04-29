from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def age_of_empires_team_generator():
    return render_template("base.html")

## run cmd: flask --app interface run
