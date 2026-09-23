from flask import Blueprint, request, jsonify
from email_validator import validate_email, EmailNotValidError
from email_service import send_verification_email
from extension import bcrypt
import secrets
auth_bp = Blueprint ("auth", __name__)
from configuration.db import get_connection

@auth_bp.route("/adduser", methods= ["POST"])
def register():
    data = request.get_json
    if not data:
        return jsonify({"success": False, "message": "Data must not be empty."})
    name = data.get("name")
    email = data.get("mail")
    password = data.get ("password")
    role = data.get ("role")

    if not name:
        return jsonify({"success": False, "message": "name cannot be empty."}), 400

    if role not in ["VENDOR", "WAITER"]:
        return jsonify({"success": False, "message": "Choose a valid role."}), 400

    if not email:
        return jsonify ({"success": False, "message": "Mail cannot be empty."})

    if not password:
        return jsonify({"success": False, "message": "password cannot be empty"})

    name = name.strip()
    email = email.strip().lower()

    if len(name) < 2:
        return jsonify({"success": False, "message": "Name must contain at least 3 character."})

    if len(name) > 100:
        return jsonify({
            "success": False, "message": "Name cannot exceed 100 character."
        })

    if len(email) > 255:
        return jsonify({
            "success": False,
            "message": "Email cannot exceed 255 character."
        })

    if len(password) < 8:
        return jsonify({
            "success": False,
            "message": "Password must contain at least 8 characters."
        })
    try:
        validate_email(email)
    except EmailNotValidError as e:
        print(f"Error: {str(e)}")

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    verification_token = secrets.token_urlsafe(32)
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (name, email, password, role, verification_token)
                VALUES (%s, %s, %s, %s, %s)
                """, (name, email, hashed_password, role, verification_token))

            conn.commit()
            verification_link = f"http://127.0.0.1:5000/={verification_token}"
            html="""
                    <html>
                        <body>
                            <h1>Welcome {name}!</h1>
                            <p>Click below to verify your account.</p>
                            <a href="{verification_link}">Verify Account</a>
                        </body>
                    </html>                    
                """
            send_verification_email(email, "Verify Email", html)

            return jsonify({
                "success": True,
                "message": "User registered successfully."
            }), 201
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if conn:
            conn.rollback()
        conn.close()
    