import json
from flask import Flask, request
import db

DB = db.DatabaseDriver()

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello world!"


# your routes here
@app.route("/api/users/")
def get_users():
    """
    Endpoint for getting all users
    """
    return json.dumps({"users": DB.get_all_users()}), 200

@app.route("/api/users/", methods = ["POST"])
def create_user():
    """
    Endpoint for creating a new user
    """
    body = json.loads(request.data)
    name = body.get("name")
    username = body.get("username")
    balance = body.get("balance", 0)
    if not name or not username: return json.dumps({"error": "missing a field"}), 400
    user_id = DB.insert_user_table(name, username, balance)
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "user not found"}), 404
    return json.dumps(user), 201

@app.route("/api/user/<int:id>/")
def get_user(id):
    """
    Endpoint for getting a user
    """
    user = DB.get_user_by_id(id)
    if user is None:
        return json.dumps({"error": "User not found"}), 404

    return json.dumps(user), 200

@app.route("/api/user/<int:id>/", methods = ["DELETE"])
def delete_user(id):
    """
    Endpoint for deleting a user
    """
    user = DB.get_user_by_id(id)
    if user is None:
        return json.dumps({"error": "User not found"}), 404
    DB.delete_user_by_id(id)

    return json.dumps(user), 200

@app.route("/api/send/", methods = ["POST"])
def send_money():
    """
    Endpoint for sending money from one user to another
    """
    body = json.loads(request.data)
    sender_id = body.get("sender_id")
    receiver_id = body.get("receiver_id")
    amount = body.get("amount")
    if  sender_id is None or receiver_id is None or amount is None:
        return json.dumps({"error": "missing a field"}), 400
    sender = DB.get_user_by_id(sender_id)
    receiver = DB.get_user_by_id(receiver_id)
    if sender is None or receiver is None or amount < 0:
        return json.dumps({"error": "User not found or amount does not exist"}), 404
    new_sender_balance = DB.get_balance_by_id(sender_id) - amount
    if new_sender_balance < 0:
        return json.dumps({"error": "overdrew sender's balance"}), 400
    DB.update_balance_by_id(sender_id, new_sender_balance)
    new_receiver_balance = DB.get_balance_by_id(receiver_id) + amount
    DB.update_balance_by_id(receiver_id, new_receiver_balance)
    return json.dumps(body), 200




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
