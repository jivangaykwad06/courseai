import os

from flask import Flask, send_from_directory

from config import Config

from routes.auth_routes import auth_bp
from routes.course_routes import course_bp
from routes.ai_routes import ai_bp
from routes.progress_routes import progress_bp
from routes.pdf_routes import pdf_bp


# =========================================================
# PATH CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FRONTEND_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "frontend")
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)

app.config.from_object(Config)


# =========================================================
# BLUEPRINTS
# =========================================================

app.register_blueprint(auth_bp)
app.register_blueprint(course_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(progress_bp)
app.register_blueprint(pdf_bp)


# =========================================================
# FRONTEND HOME
# =========================================================

@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


# =========================================================
# FRONTEND FILES
# =========================================================

@app.route("/<path:path>")
def frontend(path):

    requested_file = os.path.join(
        FRONTEND_DIR,
        path
    )

    # If requested file exists, serve it
    if os.path.isfile(requested_file):

        return send_from_directory(
            FRONTEND_DIR,
            path
        )

    # Otherwise return 404
    return {
        "success": False,
        "message": "Frontend resource not found."
    }, 404


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/api/health")
def health():

    return {
        "success": True,
        "message": "CourseAI backend is running."
    }


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def not_found(error):

    return {
        "success": False,
        "message": "Resource not found."
    }, 404


@app.errorhandler(500)
def server_error(error):

    print(
        "Internal server error:",
        repr(error)
    )

    return {
        "success": False,
        "message": "Internal server error."
    }, 500


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CourseAI - Real AI Course Builder")
    print("=" * 60)

    print(
        "Frontend:",
        FRONTEND_DIR
    )

    print(
        "Server:",
        "http://127.0.0.1:5000"
    )

    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )