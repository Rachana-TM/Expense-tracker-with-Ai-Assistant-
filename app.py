from flask import Flask, render_template, request, jsonify
import json, os
from datetime import datetime, timedelta

app = Flask(__name__)
FILE = "expenses.json"

def load_expenses():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return []

def save_expenses(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/add_expense", methods=["POST"])
def add_expense():
    data = request.get_json()
    expenses = load_expenses()

    expenses.append({
        "date": data["date"],
        "category": data["category"],
        "amount": int(data["amount"])
    })

    save_expenses(expenses)
    return jsonify({"message": "Expense added successfully"})

@app.route("/expenses_by_date/<date>")
def expenses_by_date(date):
    expenses = load_expenses()
    day = [e for e in expenses if e["date"] == date]
    total = sum(e["amount"] for e in day)
    return jsonify({"expenses": day, "total": total})

@app.route("/weekly_summary")
def weekly_summary():
    week_type = request.args.get("week", "current")
    expenses = load_expenses()  
    today = datetime.today()

    if week_type == "previous":
        start = today - timedelta(days=today.weekday() + 7)
    else:
        start = today - timedelta(days=today.weekday())

    week = {}

    for i in range(7):
        d = start + timedelta(days=i)
        week[d.strftime("%Y-%m-%d")] = 0

    for e in expenses:
        if e["date"] in week:
            week[e["date"]] += e["amount"]

    return jsonify({
        "dates": list(week.keys()),
        "totals": list(week.values())
    })

@app.route("/monthly_summary")
def monthly_summary():

    month = int(request.args.get("month"))

    expenses = load_expenses()

    today = datetime.today()
    year = today.year

    month_data = {}

    # initialize 31 days
    for i in range(1,32):
        date = f"{year}-{month:02d}-{i:02d}"
        month_data[date] = 0

    # add expense totals
    for e in expenses:
        if e["date"].startswith(f"{year}-{month:02d}"):
            month_data[e["date"]] += e["amount"]

    days = [d.split("-")[2] for d in month_data.keys()]
    totals = list(month_data.values())

    return jsonify({
        "days": days,
        "totals": totals
    })

# AI CHATBOT
@app.route("/chat", methods=["POST"])
def chat():
    q = request.get_json()["message"].lower()
    expenses = load_expenses()

    total = sum(e["amount"] for e in expenses)

    if "total" in q:
        return jsonify({"reply": f"Your total expense is ₹{total}"})

    if "today" in q:
        today = datetime.today().strftime("%Y-%m-%d")
        amt = sum(e["amount"] for e in expenses if e["date"] == today)
        return jsonify({"reply": f"You spent ₹{amt} today"})

    if "month" in q:
        month = datetime.today().strftime("%Y-%m")
        amt = sum(e["amount"] for e in expenses if e["date"].startswith(month))
        return jsonify({"reply": f"This month you spent ₹{amt}"})

    if "highest" in q:
        daily = {}
        for e in expenses:
            daily[e["date"]] = daily.get(e["date"], 0) + e["amount"]
        if daily:
            d = max(daily, key=daily.get)
            return jsonify({"reply": f"Highest spending was ₹{daily[d]} on {d}"})

    return jsonify({"reply": "🤖 Ask me about total, today, month or highest expense"})

if __name__ == "__main__":
    app.run(debug=True)