from flask import (
    Blueprint,
    jsonify,
    send_file
)

from auth import (
    login_required,
    current_user_id
)

from course_service import get_course

from pdf_service import (
    generate_course_pdf,
    safe_filename
)


pdf_bp = Blueprint(
    "pdf",
    __name__,
    url_prefix="/api/courses"
)


@pdf_bp.get("/<int:course_id>/pdf")
@login_required
def download_pdf(course_id):

    course = get_course(
        course_id,
        current_user_id()
    )

    if not course:

        return jsonify({
            "success": False,
            "message":
                "Course not found or unauthorized."
        }), 404

    try:

        from flask import session

        pdf = generate_course_pdf(
            course,
            session.get(
                "user_name",
                "User"
            )
        )

        return send_file(

            pdf,

            mimetype="application/pdf",

            as_attachment=True,

            download_name=safe_filename(
                course["title"]
            )
        )

    except Exception as error:

        print(
            "PDF error:",
            repr(error)
        )

        return jsonify({
            "success": False,
            "message":
                "PDF generation failed."
        }), 500