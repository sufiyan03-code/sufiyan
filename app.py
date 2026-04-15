import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import data_manager
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize Data
data_manager.initialize_data()

@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", role=session.get("role"))

@app.route("/admin")
def admin():
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))
    return render_template("admin.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.json
        role = data_manager.verify_user(data["username"], data["password"])
        if role:
            session["user"] = data["username"]
            session["role"] = role
            return jsonify({"success": True, "role": role})
        return jsonify({"success": False, "message": "Invalid credentials"}), 401
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        data = request.json
        try:
            data_manager.register_user(data["username"], data["password"], role="user")
            session["user"] = data["username"]
            session["role"] = "user"
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# API Endpoints
@app.route("/api/trains", methods=["GET"])
def get_trains():
    data_manager.update_train_locations()
    return jsonify(data_manager.get_trains())

@app.route("/api/trains", methods=["POST"])
def add_train():
    data = request.json
    try:
        data_manager.add_train(
            data["train_id"], 
            data["name"], 
            data["source"], 
            data["destination"], 
            data["total_seats"],
            data.get("price", 500)
        )
        return jsonify({"success": True, "message": "Train added successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/tickets", methods=["GET"])
def get_tickets():
    return jsonify(data_manager.get_tickets())

@app.route("/api/book", methods=["POST"])
def book():
    data = request.json
    try:
        pnr = data_manager.book_ticket(data["train_id"], data["passenger_name"], data["age"])
        return jsonify({"success": True, "pnr": pnr, "message": "Ticket Booked!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/cancel", methods=["POST"])
def cancel():
    data = request.json
    try:
        data_manager.cancel_ticket(data["pnr"])
        return jsonify({"success": True, "message": "Ticket Cancelled Successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
