from io import BytesIO

from reportlab.lib import colors

from reportlab.lib.enums import (
    TA_CENTER,
    TA_LEFT
)

from reportlab.lib.pagesizes import A4

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib.units import mm

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    KeepTogether,
    Table,
    TableStyle
)

from reportlab.pdfbase.ttfonts import TTFont

from reportlab.pdfbase import pdfmetrics

from reportlab.lib.colors import HexColor


def safe_filename(title):

    allowed = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        " -_"
    )

    result = "".join(
        char
        for char in title
        if char in allowed
    )

    result = result.strip()

    return (
        result[:100]
        or "CourseAI_Course"
    ) + ".pdf"


def generate_course_pdf(
    course,
    user_name
):

    buffer = BytesIO()

    document = SimpleDocTemplate(

        buffer,

        pagesize=A4,

        rightMargin=18 * mm,

        leftMargin=18 * mm,

        topMargin=20 * mm,

        bottomMargin=20 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(

        "CourseTitle",

        parent=styles["Title"],

        alignment=TA_CENTER,

        fontSize=25,

        leading=31,

        textColor=HexColor(
            "#3155D9"
        ),

        spaceAfter=20
    )

    subtitle_style = ParagraphStyle(

        "Subtitle",

        parent=styles["Normal"],

        alignment=TA_CENTER,

        fontSize=12,

        leading=18,

        textColor=colors.grey,

        spaceAfter=12
    )

    chapter_style = ParagraphStyle(

        "Chapter",

        parent=styles["Heading1"],

        fontSize=20,

        leading=25,

        textColor=HexColor(
            "#4C3CCF"
        ),

        spaceBefore=10,

        spaceAfter=12
    )

    lesson_style = ParagraphStyle(

        "Lesson",

        parent=styles["Heading2"],

        fontSize=15,

        leading=20,

        textColor=HexColor(
            "#3155D9"
        ),

        spaceBefore=12,

        spaceAfter=8
    )

    body_style = ParagraphStyle(

        "Body",

        parent=styles["BodyText"],

        fontSize=10.5,

        leading=16,

        spaceAfter=9
    )

    small_style = ParagraphStyle(

        "Small",

        parent=styles["BodyText"],

        fontSize=9,

        leading=13
    )

    story = []

    # =====================================================
    # COVER
    # =====================================================

    story.append(
        Spacer(1, 35 * mm)
    )

    story.append(
        Paragraph(
            "CourseAI",
            title_style
        )
    )

    story.append(
        Paragraph(
            "AI-Powered Personalized Learning",
            subtitle_style
        )
    )

    story.append(
        Spacer(1, 12 * mm)
    )

    story.append(
        Paragraph(
            course["title"],
            title_style
        )
    )

    story.append(
        Paragraph(
            course["description"],
            body_style
        )
    )
    story.append(
    Paragraph(
        "<b>Created by:</b> Jivan Gaykwad",
        subtitle_style
    )
)

    story.append(
    Spacer(1, 8)
)

    metadata = [

        ["Category", course["category"]],

        ["Difficulty", course["difficulty"]],

        ["Duration", course["duration"]],

        ["Name", user_name or "User"]
    ]

    table = Table(
        metadata,
        colWidths=[
            45 * mm,
            115 * mm
        ]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                HexColor("#EEF2FF")
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.7,
                HexColor("#C7D2FE")
            ),

            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.lightgrey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, -1),
                "Helvetica"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            )
        ])
    )

    story.append(table)

    story.append(
        PageBreak()
    )

    # =====================================================
    # TABLE OF CONTENTS
    # =====================================================

    story.append(
        Paragraph(
            "Table of Contents",
            chapter_style
        )
    )

    for chapter in course["chapters"]:

        story.append(
            Paragraph(
                f"Chapter {chapter['chapter_number']}: "
                f"{chapter['title']}",
                body_style
            )
        )

        for index, lesson in enumerate(
            chapter["lessons"],
            start=1
        ):

            story.append(
                Paragraph(
                    f"&nbsp;&nbsp;&nbsp;"
                    f"{index}. "
                    f"{lesson['title']}",
                    small_style
                )
            )

    story.append(
        PageBreak()
    )

    # =====================================================
    # COURSE CONTENT
    # =====================================================

    for chapter in course["chapters"]:

        story.append(
            Paragraph(
                f"Chapter "
                f"{chapter['chapter_number']}: "
                f"{chapter['title']}",
                chapter_style
            )
        )

        story.append(
            Paragraph(
                chapter["description"],
                body_style
            )
        )

        for index, lesson in enumerate(
            chapter["lessons"],
            start=1
        ):

            lesson_content = []

            lesson_content.append(
                Paragraph(
                    f"Lesson {index}: "
                    f"{lesson['title']}",
                    lesson_style
                )
            )

            content = (
                lesson["content"]
                or ""
            )

            content = content.replace(
                "\n",
                "<br/>"
            )

            lesson_content.append(
                Paragraph(
                    content,
                    body_style
                )
            )

            if lesson.get("examples"):

                lesson_content.append(
                    Paragraph(
                        "<b>Examples</b>",
                        lesson_style
                    )
                )

                examples = (
                    lesson["examples"]
                    .replace(
                        "\n",
                        "<br/>"
                    )
                )

                lesson_content.append(
                    Paragraph(
                        examples,
                        body_style
                    )
                )

            if lesson.get("quiz"):

                lesson_content.append(
                    Paragraph(
                        "Quiz",
                        lesson_style
                    )
                )

                for q_index, question in enumerate(
                    lesson["quiz"],
                    start=1
                ):

                    lesson_content.append(
                        Paragraph(
                            f"<b>Question "
                            f"{q_index}:</b> "
                            f"{question['question']}",
                            body_style
                        )
                    )

                    option_letters = [
                        "A",
                        "B",
                        "C",
                        "D"
                    ]

                    for letter, option in zip(
                        option_letters,
                        question["options"]
                    ):

                        lesson_content.append(
                            Paragraph(
                                f"{letter}. {option}",
                                small_style
                            )
                        )

                    lesson_content.append(
                        Spacer(
                            1,
                            3
                        )
                    )

            story.append(
                KeepTogether(
                    lesson_content
                )
            )

        story.append(
            PageBreak()
        )

    # =====================================================
    # END PAGE
    # =====================================================

    story.append(
        Spacer(1, 50 * mm)
    )

    story.append(
        Paragraph(
            "CourseAI",
            title_style
        )
    )

    story.append(
        Paragraph(
            "AI-Powered Personalized Learning",
            subtitle_style
        )
    )

    document.build(
        story,
        onFirstPage=_add_page_decorations,
        onLaterPages=_add_page_decorations
    )

    buffer.seek(0)

    return buffer


def _add_page_decorations(
    canvas,
    document
):

    canvas.saveState()

    width, height = A4

    canvas.setFont(
        "Helvetica",
        8
    )

    canvas.setFillColor(
        colors.grey
    )

    canvas.drawString(
    18 * mm,
    10 * mm,
    "CourseAI • Created by Jivan Gaykwad"
    )

    canvas.drawRightString(
        width - 18 * mm,
        10 * mm,
        f"Page {document.page}"
    )

    canvas.restoreState()