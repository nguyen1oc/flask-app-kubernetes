from flask import Blueprint, jsonify
from .db import get_connection
from flask import request

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return jsonify({"message": "Hello Backend OK"})

@main.route("/db")
def test_db():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"db_version": db_version[0]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/polls", methods=["GET"])
def get_polls():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM polls")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({"polls": rows})

@main.route("/create_poll", methods=["POST"])
def create_poll():
    data = request.get_json()
    question = data.get("title")

    if not question:
        return jsonify({"error": "Question is required"}), 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("INSERT INTO polls (title) VALUES (%s) RETURNING id;", (question,))
    poll_id = cur.fetchone()[0]

    cur.close()
    conn.commit()
    conn.close()

    return jsonify({"id": poll_id, "title": question}), 201

@main.route("/poll/<int:poll_id>/option", methods=["POST"])
def add_option(poll_id):
    data = request.get_json() or {}
    text = data.get("text")

    if not text:
        return jsonify({"error": "Option text is required"}), 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO options (poll_id, text) VALUES (%s, %s) RETURNING id;",
        (poll_id, text)
    )
    option_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"option_id": option_id, "text": text}), 201

@main.route("/vote", methods=["POST"])
def vote():
    data = request.get_json() or {}
    option_id = data.get("option_id")

    if not option_id:
        return jsonify({"error": "option_id is required"}), 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE options SET votes = votes + 1 WHERE id = %s RETURNING votes;",
        (option_id,)
    )

    result = cur.fetchone()

    if not result:
        return jsonify({"error": "Option not found"}), 404

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"option_id": option_id, "votes": result[0]})

@main.route("/poll/<int:poll_id>", methods=["GET"])
def get_poll(poll_id):
    conn = get_connection()
    cur = conn.cursor()

    #take poll
    cur.execute("SELECT id, title FROM polls WHERE id = %s", (poll_id,))
    poll = cur.fetchone()

    if not poll:
        return jsonify({"error": "Poll not found"}), 404

    #take options
    cur.execute(
        "SELECT id, text, votes FROM options WHERE poll_id = %s",
        (poll_id,)
    )
    options = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({
        "id": poll[0],
        "title": poll[1],
        "options": [
            {"id": o[0], "text": o[1], "votes": o[2]} for o in options
        ]
    })