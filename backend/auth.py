from functools import wraps

from flask import (
    session,
    jsonify
)


def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        user_id = session.get("user_id")

        if not user_id:

            return jsonify({
                "success": False,
                "message": "Authentication required."
            }), 401

        return function(*args, **kwargs)

    return wrapper


def current_user_id():

    return session.get("user_id")