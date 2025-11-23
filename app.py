from flask import Flask, render_template, request, redirect, url_for
import random
from categories import CATEGORIES

app = Flask(__name__)

players = []
roles = []
current_player = -1
current_item = ""
timer_minutes = 3
chosen_category = ""


@app.route("/")
def home():
    return render_template("categories.html", categories=CATEGORIES.keys())


@app.route("/choose-category", methods=["POST"])
def choose_category():
    global chosen_category
    chosen_category = request.form["category"]

    return render_template("players.html", category=chosen_category)


@app.route("/start", methods=["POST"])
def start():
    global players, roles, current_player, current_item, timer_minutes, chosen_category

    current_player = -1

    # Players
    raw = request.form["players"].strip()
    players[:] = [name.strip() for name in raw.split("\n") if name.strip()]
    if not players:
        return redirect("/")

    # Timer
    timer_minutes = int(request.form.get("timer", 3))

    # Category item
    items = CATEGORIES[request.form["category"]]
    current_item = random.choice(items)

    # Assign roles
    roles[:] = ["Spy"] + [current_item] * (len(players) - 1)
    random.shuffle(roles)

    return redirect(url_for('player'))


@app.route("/player")
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

        return render_template("role.html",
                               player_name=f"{name}, this is your role!",
                               message=role,
                               more=more)

    else:
        next_index = current_player + 1
        if next_index >= len(players):
            return redirect(url_for('game'))

        return render_template("buffer.html",
                               next_player=players[next_index])


@app.route("/game")
def game():
    return render_template("game.html",
                           timer=timer_minutes,
                           locations=CATEGORIES[chosen_category])


if __name__ == "__main__":
    app.run(debug=True)
