from flask import (
    Blueprint,
    request,
    jsonify
)

from auth import (
    login_required,
    current_user_id
)

from course_service import (
    get_user_courses,
    get_course,
    update_course,
    delete_course,
    get_dashboard_stats
)


course_bp = Blueprint(
    "courses",
    __name__,
    url_prefix="/api/courses"
)


@course_bp.get("")
@login_required
def courses():

    user_id = current_user_id()

    return jsonify({
        "success": True,
        "courses":
            get_user_courses(user_id)
    })


@course_bp.get("/<int:course_id>")
@login_required
def course(course_id):

    result = get_course(
        course_id,
        current_user_id()
    )

    if not result:

        return jsonify({
            "success": False,
            "message":
                "Course not found or you are not authorized to access it."
        }), 404

    return jsonify({
        "success": True,
        "course": result
    })


@course_bp.put("/<int:course_id>")
@login_required
def update(course_id):

    data = request.get_json(
        silent=True
    ) or {}

    required = [
        "title",
        "description",
        "category",
        "difficulty",
        "duration"
    ]

    if any(
        not str(data.get(field, "")).strip()
        for field in required
    ):

        return jsonify({
            "success": False,
            "message":
                "Please fill all required fields."
        }), 400

    updated = update_course(
        course_id,
        current_user_id(),
        data
    )

    if not updated:

        return jsonify({
            "success": False,
            "message":
                "Course not found."
        }), 404

    return jsonify({
        "success": True,
        "message":
            "Course updated successfully."
    })


@course_bp.delete("/<int:course_id>")
@login_required
def delete(course_id):

    deleted = delete_course(
        course_id,
        current_user_id()
    )

    if not deleted:

        return jsonify({
            "success": False,
            "message":
                "Course not found."
        }), 404

    return jsonify({
        "success": True,
        "message":
            "Course deleted successfully."
    })


@course_bp.get("/dashboard/stats")
@login_required
def stats():

    return jsonify({
        "success": True,
        "stats":
            get_dashboard_stats(
                current_user_id()
            )
    })