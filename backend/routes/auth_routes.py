from flask import (
    Blueprint,
    request,
    jsonify,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from db import get_connection


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


@auth_bp.post("/register")
def register():

    data = request.get_json(
        silent=True
    ) or {}

    full_name = data.get(
        "full_name",
        ""
    ).strip()

    email = data.get(
        "email",
        ""
    ).strip().lower()

    password = data.get(
        "password",
        ""
    )

    role = data.get(
        "role",
        "student"
    )

    if not full_name or not email or not password:

        return jsonify({
            "success": False,
            "message":
                "Please fill all required fields."
        }), 400

    if len(password) < 8:

        return jsonify({
            "success": False,
            "message":
                "Password must contain at least 8 characters."
        }), 400

    if role not in (
        "student",
        "instructor"
    ):

        role = "student"

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        if cursor.fetchone():

            return jsonify({
                "success": False,
                "message":
                    "An account with this email already exists."
            }), 409

        password_hash = generate_password_hash(
            password
        )

        cursor.execute(
            """
            INSERT INTO users
            (
                full_name,
                email,
                password_hash,
                role
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                full_name,
                email,
                password_hash,
                role
            )
        )

        connection.commit()

        user_id = cursor.lastrowid

        return jsonify({
            "success": True,
            "message":
                "Registration successful.",
            "user": {
                "id": user_id,
                "full_name": full_name,
                "email": email,
                "role": role
            }
        }), 201

    finally:

        cursor.close()

        connection.close()


@auth_bp.post("/login")
def login():

    data = request.get_json(
        silent=True
    ) or {}

    email = data.get(
        "email",
        ""
    ).strip().lower()

    password = data.get(
        "password",
        ""
    )

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                id,
                full_name,
                email,
                password_hash,
                role
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if (
            not user
            or not check_password_hash(
                user["password_hash"],
                password
            )
        ):

            return jsonify({
                "success": False,
                "message":
                    "Invalid email or password."
            }), 401

        session.clear()

        session["user_id"] = user["id"]

        session["user_name"] = user["full_name"]

        session["user_email"] = user["email"]

        session["user_role"] = user["role"]

        return jsonify({
            "success": True,
            "message":
                "Login successful.",
            "user": {
                "id": user["id"],
                "full_name": user["full_name"],
                "email": user["email"],
                "role": user["role"]
            }
        })

    finally:

        cursor.close()

        connection.close()


@auth_bp.post("/logout")
def logout():

    session.clear()

    return jsonify({
        "success": True,
        "message":
            "Logged out successfully."
    })


@auth_bp.get("/me")
def me():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "success": False,
            "authenticated": False
        })

    return jsonify({
        "success": True,
        "authenticated": True,
        "user": {
            "id":
                user_id,

            "full_name":
                session.get("user_name"),

            "email":
                session.get("user_email"),

            "role":
                session.get("user_role")
        }
    })