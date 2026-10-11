from flask import (
    Blueprint,
    request,
    jsonify
)

from auth import (
    login_required,
    current_user_id
)

from db import get_connection


progress_bp = Blueprint(
    "progress",
    __name__,
    url_prefix="/api/progress"
)


@progress_bp.post("")
@login_required
def update_progress():

    data = request.get_json(
        silent=True
    ) or {}

    course_id = data.get(
        "course_id"
    )

    lesson_id = data.get(
        "lesson_id"
    )

    completed = bool(
        data.get(
            "completed",
            True
        )
    )

    if not course_id or not lesson_id:

        return jsonify({
            "success": False,
            "message":
                "Course ID and lesson ID are required."
        }), 400

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO course_progress
            (
                user_id,
                course_id,
                lesson_id,
                completed
            )
            VALUES (%s, %s, %s, %s)

            ON DUPLICATE KEY UPDATE

                completed = VALUES(completed),

                updated_at = CURRENT_TIMESTAMP
            """,
            (
                current_user_id(),
                course_id,
                lesson_id,
                completed
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message":
                "Progress updated successfully."
        })

    finally:

        cursor.close()

        connection.close()


@progress_bp.get("/<int:course_id>")
@login_required
def get_progress(course_id):

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                lesson_id,
                completed
            FROM course_progress
            WHERE user_id = %s
            AND course_id = %s
            """,
            (
                current_user_id(),
                course_id
            )
        )

        rows = cursor.fetchall()

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM lessons l

            INNER JOIN chapters ch
                ON ch.id = l.chapter_id

            INNER JOIN courses c
                ON c.id = ch.course_id

            WHERE c.id = %s
            AND c.user_id = %s
            """,
            (
                course_id,
                current_user_id()
            )
        )

        total = cursor.fetchone()[
            "total"
        ]

        completed = sum(
            1
            for row in rows
            if row["completed"]
        )

        percentage = (
            round(
                completed * 100 / total
            )
            if total
            else 0
        )

        return jsonify({
            "success": True,

            "completed_lessons": [
                row["lesson_id"]
                for row in rows
                if row["completed"]
            ],

            "completed":
                completed,

            "total":
                total,

            "percentage":
                percentage
        })

    finally:

        cursor.close()

        connection.close()