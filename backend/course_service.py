import json

from db import get_connection


def create_course_from_ai(
    user_id,
    generated
):

    connection = get_connection()

    cursor = connection.cursor()

    try:

        course = generated.course

        cursor.execute(
            """
            INSERT INTO courses
            (
                user_id,
                title,
                description,
                category,
                difficulty,
                duration
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                course.title,
                course.description,
                course.category,
                course.difficulty,
                course.duration
            )
        )

        course_id = cursor.lastrowid

        for chapter in generated.chapters:

            cursor.execute(
                """
                INSERT INTO chapters
                (
                    course_id,
                    chapter_number,
                    title,
                    description
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    course_id,
                    chapter.chapter_number,
                    chapter.title,
                    chapter.description
                )
            )

            chapter_id = cursor.lastrowid

            for lesson in chapter.lessons:

                quiz_data = [

                    {
                        "question":
                            question.question,

                        "options":
                            question.options,

                        "answer":
                            question.answer
                    }

                    for question
                    in lesson.quiz
                ]

                cursor.execute(
                    """
                    INSERT INTO lessons
                    (
                        chapter_id,
                        title,
                        content,
                        examples,
                        quiz
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        chapter_id,
                        lesson.title,
                        lesson.content,
                        lesson.examples,
                        json.dumps(
                            quiz_data,
                            ensure_ascii=False
                        )
                    )
                )

        connection.commit()

        return course_id

    except Exception:

        connection.rollback()

        raise

    finally:

        cursor.close()

        connection.close()


def get_user_courses(user_id):

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                c.id,
                c.title,
                c.description,
                c.category,
                c.difficulty,
                c.duration,
                c.created_at,
                c.updated_at,

                COUNT(DISTINCT l.id)
                    AS total_lessons,

                COUNT(
                    DISTINCT CASE
                        WHEN cp.completed = 1
                        THEN cp.lesson_id
                    END
                ) AS completed_lessons

            FROM courses c

            LEFT JOIN chapters ch
                ON ch.course_id = c.id

            LEFT JOIN lessons l
                ON l.chapter_id = ch.id

            LEFT JOIN course_progress cp
                ON cp.course_id = c.id
                AND cp.lesson_id = l.id
                AND cp.user_id = c.user_id

            WHERE c.user_id = %s

            GROUP BY
                c.id

            ORDER BY
                c.created_at DESC
            """,
            (user_id,)
        )

        courses = cursor.fetchall()

        for course in courses:

            total = course["total_lessons"] or 0

            completed = course["completed_lessons"] or 0

            course["progress"] = (
                round(
                    completed * 100 / total
                )
                if total
                else 0
            )

        return courses

    finally:

        cursor.close()

        connection.close()


def get_course(
    course_id,
    user_id
):

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                id,
                title,
                description,
                category,
                difficulty,
                duration,
                created_at,
                updated_at
            FROM courses
            WHERE id = %s
            AND user_id = %s
            """,
            (
                course_id,
                user_id
            )
        )

        course = cursor.fetchone()

        if not course:

            return None

        cursor.execute(
            """
            SELECT
                id,
                chapter_number,
                title,
                description
            FROM chapters
            WHERE course_id = %s
            ORDER BY chapter_number
            """,
            (course_id,)
        )

        chapters = cursor.fetchall()

        for chapter in chapters:

            cursor.execute(
                """
                SELECT
                    id,
                    title,
                    content,
                    examples,
                    quiz,
                    created_at
                FROM lessons
                WHERE chapter_id = %s
                ORDER BY id
                """,
                (chapter["id"],)
            )

            lessons = cursor.fetchall()

            for lesson in lessons:

                if isinstance(
                    lesson["quiz"],
                    str
                ):

                    try:

                        lesson["quiz"] = json.loads(
                            lesson["quiz"]
                        )

                    except json.JSONDecodeError:

                        lesson["quiz"] = []

                elif lesson["quiz"] is None:

                    lesson["quiz"] = []

            chapter["lessons"] = lessons

        course["chapters"] = chapters

        return course

    finally:

        cursor.close()

        connection.close()


def update_course(
    course_id,
    user_id,
    data
):

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE courses
            SET
                title = %s,
                description = %s,
                category = %s,
                difficulty = %s,
                duration = %s
            WHERE id = %s
            AND user_id = %s
            """,
            (
                data["title"],
                data["description"],
                data["category"],
                data["difficulty"],
                data["duration"],
                course_id,
                user_id
            )
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:

        cursor.close()

        connection.close()


def delete_course(
    course_id,
    user_id
):

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM courses
            WHERE id = %s
            AND user_id = %s
            """,
            (
                course_id,
                user_id
            )
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:

        cursor.close()

        connection.close()


def get_dashboard_stats(user_id):

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_courses
            FROM courses
            WHERE user_id = %s
            """,
            (user_id,)
        )

        total_courses = cursor.fetchone()[
            "total_courses"
        ]

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_lessons
            FROM lessons l

            INNER JOIN chapters ch
                ON ch.id = l.chapter_id

            INNER JOIN courses c
                ON c.id = ch.course_id

            WHERE c.user_id = %s
            """,
            (user_id,)
        )

        total_lessons = cursor.fetchone()[
            "total_lessons"
        ]

        cursor.execute(
            """
            SELECT
                COUNT(*) AS completed_lessons
            FROM course_progress cp

            INNER JOIN courses c
                ON c.id = cp.course_id

            WHERE cp.user_id = %s
            AND cp.completed = 1
            """,
            (user_id,)
        )

        completed_lessons = cursor.fetchone()[
            "completed_lessons"
        ]

        cursor.execute(
            """
            SELECT COUNT(*) AS completed_courses

            FROM courses c

            WHERE c.user_id = %s

            AND NOT EXISTS (

                SELECT 1

                FROM chapters ch

                INNER JOIN lessons l
                    ON l.chapter_id = ch.id

                LEFT JOIN course_progress cp

                    ON cp.lesson_id = l.id
                    AND cp.course_id = c.id
                    AND cp.user_id = c.user_id

                WHERE ch.course_id = c.id

                AND (
                    cp.completed IS NULL
                    OR cp.completed = 0
                )
            )
            """,
            (user_id,)
        )

        completed_courses = cursor.fetchone()[
            "completed_courses"
        ]

        return {
            "total_courses":
                total_courses,

            "completed_courses":
                completed_courses,

            "in_progress":
                max(
                    total_courses -
                    completed_courses,
                    0
                ),

            "lessons_completed":
                completed_lessons,

            "total_lessons":
                total_lessons
        }

    finally:

        cursor.close()

        connection.close()