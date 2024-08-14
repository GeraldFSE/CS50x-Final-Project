import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, sgd
import calendar
from datetime import datetime
import random


# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["sgd"] = sgd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///budget.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    if request.method == "POST":
        date = request.form.get("date")

        if not request.form.get("date"):
            return render_template("index.html", errormessage="Do not leave date field empty!")

        year = int(date[:4])
        month = int(date[5:])

        rows = db.execute(
            "SELECT * FROM budget WHERE year=? AND month=? AND id=?", year, month, session["user_id"]
        )

        if len(rows) != 1:
            month_name = calendar.month_name[month]
            return render_template("changebudget.html", month=month_name, year=year, date=date)

        else:
            breakdown = db.execute(
                "SELECT * FROM breakdown WHERE year=? AND month=? AND id=?", year, month, session["user_id"]
            )

            total_spending = 0.0
            grandtotal = 0.0
            budget = float(rows[0]["budget"])
            grandtotal = grandtotal + budget
            budget = sgd(budget)

            for item in breakdown:
                total_spending = total_spending + float(item["cost"])
                item["cost"] = sgd(item["cost"])

            grandtotal = grandtotal + total_spending

            total_spending = sgd(total_spending)
            grandtotal = sgd(grandtotal)

            date_obj = datetime.strptime(date, "%Y-%m")
            formatted_date = date_obj.strftime("%B %Y")

            sorted_breakdown = sorted(breakdown, key=lambda x: x['day'])
            return render_template("index.html", checker=True, breakdown=sorted_breakdown, formatted_date=formatted_date, totalspending=total_spending, budget=budget, grandtotal=grandtotal)

    return render_template("index.html", checker=False)


@app.route("/breakdown", methods=["GET", "POST"])
@login_required
def breakdown():

    if request.method == "POST":
        date = request.form.get("date")

        if not request.form.get("date"):
            return render_template("addbreakdown.html", errormessage="Please do not leave date field empty")

        year, month, day = date.split("-")
        year = int(year)
        month = int(month)
        day = int(day)
        title = request.form.get("title")
        description = request.form.get("description")

        if not request.form.get("cost"):
            return render_template("addbreakdown.html", errormessage="Please do not leave cost field empty")

        cost = float(request.form.get("cost"))

        if cost <= 0.0:
            return render_template("addbreakdown.html", errormessage="Cost must be more than 0")

        if not request.form.get("title"):
            return render_template("addbreakdown.html", errormessage="Please do not leave title field empty")

        if not request.form.get("description"):
            description = "NIL"

        if title[0].isalpha():
            title = title[0].upper() + title[1:]

        if description[0].isalpha():
            description = description[0].upper() + description[1:]

        db.execute("INSERT INTO breakdown (day, month, year, cost, title, description, id) VALUES (?, ?, ? , ?, ?, ?, ?)",
                   day, month, year, cost, title, description, session["user_id"])

        budget = db.execute("SELECT * FROM budget WHERE id=? AND month=? AND year=?",
                            session["user_id"], month, year)

        budget = float(budget[0]["budget"])

        new_budget = budget - cost

        if new_budget < 0.0:
            return render_template("addbreakdown.html", errormessage="Error! Spending is over budget!")

        db.execute("UPDATE budget SET budget=? WHERE id=? AND month=? AND year=?",
                   new_budget, session["user_id"], month, year)

        strdate = str(year) + "-" + str(month)
        flash("New breakdown added!")
        return render_template("redirect.html", date=strdate)

    return render_template("addbreakdown.html")


@app.route("/budget", methods=["GET", "POST"])
@login_required
def budget():
    if request.method == "POST":
        date = request.form.get("date")

        if not request.form.get("date"):
            return render_template("changebudget.html", errormessage="Please do not leave date field empty")

        budget = request.form.get("budget")

        year = int(date[:4])
        month = int(date[5:])

        if not request.form.get("budget"):
            return render_template("changebudget.html", errormessage="Please do not leave budget field empty")

        budget = float(budget)

        rows = db.execute(
            "SELECT * FROM budget WHERE year=? AND month=? AND id=?", year, month, session["user_id"]
        )

        if len(rows) != 1:

            if budget <= 0.0:
                month_name = calendar.month_name[month]

                return render_template("changebudget.html", errormessage="Budget must be more than 0", month=month_name, year=year, date=date)

            db.execute("INSERT INTO budget (year, month, budget,id) VALUES (?, ?, ?,?)",
                       year, month, budget, session["user_id"])
            flash("Budget added for new month!")
            return render_template("redirect.html", date=date)

        else:
            if budget <= 0.0:
                return render_template("changebudget.html", errormessage="Budget must be more than 0")

            db.execute("UPDATE budget SET budget=? WHERE year=? AND month=? and id=?",
                       budget, year, month, session["user_id"])

            flash("Exisiting Budget Changed!")
            return render_template("redirect.html", date=date)

    return render_template("changebudget.html")


@app.route("/check-database", methods=["POST"])
@login_required
def check_database():
    """for change budget"""
    if request.method == "POST":
        date = request.form.get("date")

        if not request.form.get("date"):
            return jsonify({"error": "Date field is required."}), 400

        year = int(date[:4])
        month = int(date[5:])

        rows = db.execute(
            "SELECT * FROM budget WHERE year=? AND month=? AND id=?", year, month, session["user_id"]
        )

        if len(rows) != 1:
            return jsonify({'exists': False})

        else:
            return jsonify({'exists': True})


@app.route("/check-database1", methods=["POST"])
@login_required
def check_database1():
    """for add breakdown"""
    if request.method == "POST":
        date = request.form.get("date")

        if not request.form.get("date"):
            return jsonify({"error": "Date field is required."}), 400

        year, month, day = date.split("-")
        year = int(year)
        month = int(month)
        day = int(day)

        rows = db.execute(
            "SELECT * FROM budget WHERE year=? AND month=? AND id=?", year, month, session["user_id"]
        )

        if len(rows) != 1:
            return jsonify({'exists': False})

        else:
            return jsonify({'exists': True})


@app.route("/editbreakdown", methods=["POST"])
@login_required
def editbreakdown():
    if request.method == "POST":
        breakdownid = int(request.form.get("breakdownid"))
        month = int(request.form.get("month"))
        year = int(request.form.get("year"))

        if not request.form.get("checker"):
            return render_template("editbreakdown.html", breakdownid=breakdownid, month=month, year=year)

        else:

            title = request.form.get("title")
            description = request.form.get("description")

            if not request.form.get("cost"):
                return render_template("editbreakdown.html", errormessage="Please do not leave cost field empty")

            cost = float(request.form.get("cost"))

            if cost <= 0.0:
                return render_template("editbreakdown.html", errormessage="Cost must be more than 0")

            if not request.form.get("title"):
                return render_template("editbreakdown.html", errormessage="Please do not leave title field empty")

            if not request.form.get("description"):
                description = "NIL"

            if title[0].isalpha():
                title = title[0].upper() + title[1:]

            if description[0].isalpha():
                description = description[0].upper() + description[1:]

            rows = db.execute("SELECT * FROM budget WHERE year=? AND month=? AND id=?",
                              year, month, session["user_id"])

            breakdown = db.execute(
                "SELECT * FROM breakdown WHERE breakdownid=? AND id=?", breakdownid, session["user_id"])

            difference = cost - float(breakdown[0]["cost"])
            new_budget = float(rows[0]["budget"]) - float(difference)

            if new_budget < 0.0:
                return render_template("editbreakdown.html", errormessage="Error! Spending is over budget!")

            db.execute("UPDATE budget SET budget=? WHERE id=? AND month=? AND year=?",
                       new_budget, session["user_id"], month, year)

            db.execute("UPDATE breakdown SET title=?, cost=?, description= ? WHERE id=? AND breakdownid=?",
                       title, cost, description, session["user_id"], breakdownid)

            date = str(year) + "-" + str(month)
            return render_template("redirect.html", date=date)


@app.route("/deletebreakdown", methods=["POST"])
@login_required
def deletebreakdown():
    if request.method == "POST":
        breakdownid = int(request.form.get("breakdownid"))
        month = int(request.form.get("month"))
        year = int(request.form.get("year"))

        breakdown = db.execute(
            "SELECT * FROM breakdown WHERE breakdownid=? AND id=?", breakdownid, session["user_id"])

        rows = db.execute("SELECT * FROM budget WHERE year=? AND month=? AND id=?",
                          year, month, session["user_id"])

        new_budget = float(rows[0]["budget"]) + float(breakdown[0]["cost"])

        db.execute("UPDATE budget SET budget=? WHERE id=? AND month=? AND year=?",
                   new_budget, session["user_id"], month, year)

        db.execute("DELETE FROM breakdown WHERE id=? AND breakdownid =?",
                   session["user_id"], breakdownid)
        date = str(year) + "-" + str(month)
        return render_template("redirect.html", date=date)


@app.route("/barchart", methods=["GET", "POST"])
@login_required
def barchart():

    return render_template("barchart.html")


@app.route("/barchartdata", methods=["POST"])
@login_required
def barchartdata():

    start = request.form.get("start")
    if not request.form.get("start"):
        return jsonify({"error": "Start date field is required."}), 400

    startyear = int(start[:4])
    startmonth = int(start[5:])

    end = request.form.get("end")
    if not request.form.get("end"):
        return jsonify({"error": "End date field is required."}), 400

    endyear = int(end[:4])
    endmonth = int(end[5:])

    if startyear == endyear:
        if (endmonth - startmonth) < 0:
            return jsonify({"error": "End date must be after start date"}), 400

    elif endyear < startyear:
        return jsonify({"error": "End date must be after start date"}), 400

    currentyear = startyear
    currentmonth = startmonth
    datelist = []
    costlist = []

    while (currentyear < endyear) or (currentyear == endyear and currentmonth <= endmonth):

        totalbreakdown = 0.0

        rows = db.execute(
            "SELECT * FROM breakdown WHERE year=? AND month=? AND id=?", currentyear, currentmonth, session["user_id"]
        )

        for item in rows:
            totalbreakdown = totalbreakdown + float(item["cost"])

        month_name = calendar.month_name[currentmonth]
        str_date = month_name + " " + str(currentyear)

        datelist.append(str_date)
        costlist.append(float(round(totalbreakdown, 2)))

        if currentmonth == 12:
            currentmonth = 1
            currentyear += 1
        else:
            currentmonth += 1

    barchartdata = {
        'date': datelist,
        'spend': costlist
    }

    return jsonify(barchartdata)


@app.route("/piechart", methods=["GET", "POST"])
@login_required
def piechart():

    return render_template("piechart.html")


@app.route("/piechartdata", methods=["POST"])
@login_required
def piechartdata():

    date = request.form.get("date")
    if not request.form.get("date"):
        return jsonify({"error": "Date field is required."}), 400

    dateyear = int(date[:4])
    datemonth = int(date[5:])

    rows = db.execute(
        "SELECT * FROM breakdown WHERE year=? AND month=? AND id=?", dateyear, datemonth, session["user_id"]
    )

    repeatlist = []

    labelslist = []
    datalist = []
    backgroundlist = []

    for item in rows:
        name = item["title"]
        name_upper = name.upper()

        if name_upper not in repeatlist:

            spending = float(item["cost"])
            checker_spending = 0.0

            for checker in rows:

                checker_name = checker["title"]
                checker_upper = checker_name.upper()

                if checker_upper == name_upper:
                    checker_spending = checker_spending + float(checker["cost"])

            if checker_spending != spending:
                repeatlist.append(name_upper)
                spending = checker_spending

            if name[0].isalpha():
                name = name[0].capitalize() + name[1:]

            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)

            background = str("rgb(" + str(r) + ", " + str(g) + ", " + str(b) + ")")

            while background in backgroundlist:

                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)

                background = str("rgb(" + str(r) + ", " + str(g) + ", " + str(b) + ")")

            labelslist.append(name)
            datalist.append(spending)
            backgroundlist.append(background)

    piechartdata = {
        'labels': labelslist,
        'data': datalist,
        'backgroundcolor': backgroundlist
    }

    return jsonify(piechartdata)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", errormessage="Must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", errormessage="Must provide password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return render_template("login.html", errormessage="Invalid password or username")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Welcome, "+request.form.get("username")+"!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            return render_template("register.html", errormessage="Must provide username")

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        if len(rows) != 0:
            return render_template("register.html", errormessage="Username Exists")

        if not request.form.get("password") or not request.form.get("confirmation"):
            return render_template("register.html", errormessage="Must provide password and confirmation password")

        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html", errormessage="Password and confirmation password do not match")

        password = request.form.get("password")
        hashed_password = generate_password_hash(password)

        db.execute("INSERT INTO users (username,hash) VALUES (?,?)",
                   request.form.get("username"), hashed_password)

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        session["user_id"] = rows[0]["id"]

        flash("Successfully Registered!")
        return redirect("/")

    return render_template("register.html")
