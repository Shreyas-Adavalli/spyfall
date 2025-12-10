from flask import Flask, render_template, request, redirect, session, url_for
import random
from categories import CATEGORIES
import os


# WL Aes and concept changes (Last definitely working commit)

app = Flask(__name__)
app.secret_key = "apasswordineedforsomereason" 

players = []
roles = []
current_player = -1
current_item = ""
timer_minutes = 3
chosen_category = ""

@app.route("/")
def home():
    return render_template("home.html")   # Homepage for selecting game

@app.route("/spyfall")
def spyfall_home():
    previous_players = session.get("players_text", "")
    return render_template("spyfall/categories.html",
                           categories=CATEGORIES.keys(),
                           previous_players=previous_players)


@app.route("/spyfall/choose-category", methods=["POST"])
def choose_category():
    global chosen_category
    chosen_category = request.form["category"]

    # Pass previously used names to the players screen
    previous_players = session.get("players_text", "")

    return render_template("spyfall/players.html",
                           category=chosen_category,
                           previous_players=previous_players)


@app.route("/spyfall/start", methods=["POST"])
def start():
    global players, roles, current_player, current_item, timer_minutes, chosen_category

    current_player = -1

    # Players
    raw = request.form["players"].strip()
    players[:] = [name.strip() for name in raw.split("\n") if name.strip()]
    if not players:
        return redirect("/")

    # Store the raw player string in session so we can reuse later
    session["players_text"] = raw

    # Timer
    timer_minutes = int(request.form.get("timer", 3))

    # Category item
    items = CATEGORIES[request.form["category"]]
    current_item = random.choice(items)

    # Assign roles
    roles[:] = ["Spy"] + [current_item] * (len(players) - 1)
    random.shuffle(roles)

    return redirect(url_for('player'))


@app.route("/spyfall/player")
def player():
    global current_player

    show_role = request.args.get("reveal") == "1"

    if show_role:
        current_player += 1

        # Finished showing all roles
        if current_player >= len(players):
            return redirect(url_for('game'))

        name = players[current_player]
        role = roles[current_player]
        more = current_player < len(players) - 1

        return render_template("spyfall/role.html",
                               player_name=f"{name}, this is your role!",
                               message=role,
                               more=more)

    else:
        next_index = current_player + 1
        if next_index >= len(players):
            return redirect(url_for('game'))

        return render_template("spyfall/buffer.html",
                               next_player=players[next_index])


@app.route("/spyfall/game")
def game():
    return render_template("spyfall/game.html",
                           timer=timer_minutes,
                           locations=CATEGORIES[chosen_category])




@app.route("/wavelength")
def wavelength_home():
    return render_template("wavelength/home.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port)
