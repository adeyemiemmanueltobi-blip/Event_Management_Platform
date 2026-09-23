from flask import Flask, config, render_template, request, jsonify
from email_validation import validate_email, EmailNotValidError
from configuration.db import get_connection
from extension import bcrypt
app = Flask(__name__)

bcrypt.init_app(app)
app.config.from_object(config)
@app.route("/")
def check_connection():
    conn = None

    try:
        conn = get_connection()

        if conn:
            return "<h1>MySQL Connection successful!</h1>"
        
        return "<h1>MySQL Connection failed!</h1>"

    except Exception as e:
        return f"<h1>connection error: {e}</h1>"

    finally:
        if conn:
            conn.close()

@app.route("/users")
def home():
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:   # dictionary=True is required
            cursor.execute("SELECT * FROM users")
            all_users = cursor.fetchall()
            return render_template("app.html", users=all_users)
    except Exception as e:
        print(f"Error occurred: {e}")
        return f"<h1>Error: {e}</h1>"
    finally:
        if conn:
            conn.close()

@app. route("/adduser", methods= ["POST"])
def add_user():
    data = request.json
    lname = data ["Lastname"]
    fname = data.get("firstname")
    mail = data.get("mail")
    password = data.get("password")
    role = data.get("role")

    if not lname.strip():
        if not lname or len(lname) < 3:
            return jsonify({f"success": False, "message": "Lastname cannot be empty or abbreviated."}),
    if not fname.strip():
        if not fname or len(lname) < 3:
            return jsonify({"success": False, "message": "Firstname cannot be empty or abbreviated."})

    if not mail:
        return jsonify({"success": False, "message": "Mail cannot be empty."})
    if not password:
        return jsonify({"success": False, "message": "Password cannot be empty."})
    try:
        valid_email = validate_email(mail)
        mail = valid_email.normalized
    except EmailNotValidError as e:
        return jsonify({"message": str(e)}), 400

    if not password:
        return jsonify({"success": False, "message": "Password cannot be empty."})

    password = bcrypt.generate_password_hash(password)
    conn = None
    try:
        conn = get_connection()
        with conn. cursor() as cursor:
            cursor. execute(
                """
                INSERT INTO users(lastname, firstname, email, role) VALUES
                (%s, %s, %s,%s)
                """, (lname, fname, mail, role)
            )
            conn. commit()
            return jsonify({"success": True, "message": "User added successfully"}), 201
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {e}"}), 500
if __name__ == "__main__":
    app.run(debug=True)