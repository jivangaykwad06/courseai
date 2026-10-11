from flask import (
    Blueprint,
    request,
    jsonify
)

from auth import (
    login_required,
    current_user_id
)

from ai_service import generate_course

from course_service import (
    create_course_from_ai
)


ai_bp = Blueprint(
    "ai",
    __name__,
    url_prefix="/api/ai"
)


@ai_bp.post("/generate-course")
@login_required
def generate():

    data = request.get_json(
        silent=True
    ) or {}

    title = data.get(
        "title",
        ""
    ).strip()

    category = data.get(
        "category",
        ""
    ).strip()

    difficulty = data.get(
        "difficulty",
        "Beginner"
    )

    duration = data.get(
        "duration",
        ""
    ).strip()

    chapter_count = data.get(
        "chapter_count",
        5
    )

    requirements = data.get(
        "requirements",
        ""
    ).strip()

    if not title:

        return jsonify({
            "success": False,
            "message":
                "Course title is required."
        }), 400

    if not category:

        return jsonify({
            "success": False,
            "message":
                "Course category is required."
        }), 400

    if not duration:

        return jsonify({
            "success": False,
            "message":
                "Course duration is required."
        }), 400

    try:

        chapter_count = int(
            chapter_count
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({
            "success": False,
            "message":
                "Chapter count must be a number."
        }), 400

    if chapter_count < 1 or chapter_count > 20:

        return jsonify({
            "success": False,
            "message":
                "Chapter count must be between 1 and 20."
        }), 400

    try:

        generated = generate_course(

            title=title,

            category=category,

            difficulty=difficulty,

            duration=duration,

            chapter_count=chapter_count,

            requirements=requirements
        )

        course_id = create_course_from_ai(

            current_user_id(),

            generated
        )

        return jsonify({
            "success": True,
            "message":
                "Course generated successfully.",

            "course_id":
                course_id
        }), 201

    except Exception as error:

        print(
            "AI generation error:",
            repr(error)
        )

        return jsonify({
            "success": False,
            "message":
                "Course generation failed. "
                "Please check your Gemini API configuration "
                "and try again."
        }), 500