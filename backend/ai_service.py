
from typing import List
import time

from google import genai

from pydantic import (
    BaseModel,
    Field
)

from config import Config


# =========================================================
# PYDANTIC AI SCHEMA
# =========================================================

class QuizQuestion(BaseModel):

    question: str

    options: List[str] = Field(
        min_length=4,
        max_length=4
    )

    answer: str


class Lesson(BaseModel):

    title: str

    content: str

    examples: str

    quiz: List[QuizQuestion]


class Chapter(BaseModel):

    chapter_number: int

    title: str

    description: str

    lessons: List[Lesson]


class CourseInfo(BaseModel):

    title: str

    description: str

    category: str

    difficulty: str

    duration: str


class GeneratedCourse(BaseModel):

    course: CourseInfo

    chapters: List[Chapter]


# =========================================================
# GEMINI CLIENT
# =========================================================

if not Config.GEMINI_API_KEY:

    raise RuntimeError(
        "GEMINI_API_KEY is missing from .env"
    )


client = genai.Client(
    api_key=Config.GEMINI_API_KEY
)


# =========================================================
# TEMPORARY GEMINI ERROR CHECK
# =========================================================

def is_retryable_error(error):

    error_text = str(error).lower()

    retry_messages = [
        "503",
        "unavailable",
        "high demand",
        "429",
        "resource exhausted",
        "rate limit",
        "too many requests",
        "temporarily unavailable",
        "internal server error"
    ]

    return any(
        message in error_text
        for message in retry_messages
    )


# =========================================================
# GENERATE COURSE
# =========================================================

def generate_course(
    title,
    category,
    difficulty,
    duration,
    chapter_count,
    requirements
):

    prompt = f"""
You are an expert educational course designer.

Create a complete high-quality learning course.

COURSE TITLE:
{title}

CATEGORY:
{category}

DIFFICULTY:
{difficulty}

DURATION:
{duration}

NUMBER OF CHAPTERS:
{chapter_count}

ADDITIONAL REQUIREMENTS:
{requirements or "None"}

IMPORTANT REQUIREMENTS:

1. Generate exactly {chapter_count} chapters.

2. Do not use generic placeholder text.

3. Every chapter must contain meaningful lessons.

4. Every lesson must contain:
   - title
   - detailed educational content
   - practical examples
   - exactly 3 useful MCQ questions

5. Every MCQ must have exactly 4 options.

6. The answer must exactly match one of
   the four options.

7. Course content must be appropriate for
   the selected difficulty.

8. Content should be useful for an engineering
   college student.

9. Avoid repeated chapters and repeated lessons.

10. Use clear educational English.

11. Include practical examples wherever useful.

12. Make the content detailed enough for actual
    self-study.

13. Return only structured JSON matching the
    requested schema.
"""

    # =====================================================
    # AUTOMATIC RETRY
    # =====================================================

    max_attempts = 4

    last_error = None

    for attempt in range(1, max_attempts + 1):

        try:

            print(
                f"Gemini generation attempt "
                f"{attempt}/{max_attempts}..."
            )

            response = client.models.generate_content(

                model=Config.GEMINI_MODEL,

                contents=prompt,

                config={
                    "response_mime_type": "application/json",

                    "response_schema":
                        GeneratedCourse
                }
            )

            # =================================================
            # CHECK RESPONSE
            # =================================================

            if not response.parsed:

                raise ValueError(
                    "Gemini returned invalid structured data."
                )

            generated = response.parsed

            # =================================================
            # VALIDATE GENERATED COURSE
            # =================================================

            validate_generated_course(
                generated,
                chapter_count
            )

            print(
                "Gemini course generation successful."
            )

            return generated

        except Exception as error:

            last_error = error

            print(
                f"Gemini generation error "
                f"on attempt {attempt}: {error}"
            )

            # =================================================
            # RETRY ONLY TEMPORARY ERRORS
            # =================================================

            if not is_retryable_error(error):

                raise

            # No retry after final attempt

            if attempt == max_attempts:

                break

            # Exponential backoff:
            #
            # Attempt 1 -> wait 2 seconds
            # Attempt 2 -> wait 4 seconds
            # Attempt 3 -> wait 8 seconds

            wait_time = 2 ** attempt

            print(
                f"Gemini temporarily unavailable. "
                f"Retrying in {wait_time} seconds..."
            )

            time.sleep(wait_time)

    # =========================================================
    # ALL RETRIES FAILED
    # =========================================================

    raise RuntimeError(
        "Gemini AI is temporarily unavailable. "
        "Please try generating the course again "
        "after a short while."
    ) from last_error


# =========================================================
# VALIDATION
# =========================================================

def validate_generated_course(
    course,
    expected_chapters
):

    if not course.course.title:

        raise ValueError(
            "AI generated course title is empty."
        )

    if not course.course.description:

        raise ValueError(
            "AI generated course description is empty."
        )

    if len(course.chapters) != expected_chapters:

        raise ValueError(
            "AI returned an incorrect number of chapters."
        )

    for index, chapter in enumerate(
        course.chapters,
        start=1
    ):

        if chapter.chapter_number != index:

            raise ValueError(
                f"Chapter numbering is invalid. "
                f"Expected {index}."
            )

        if not chapter.title:

            raise ValueError(
                "Chapter title is missing."
            )

        if not chapter.description:

            raise ValueError(
                f"Chapter '{chapter.title}' "
                f"has no description."
            )

        if not chapter.lessons:

            raise ValueError(
                f"Chapter '{chapter.title}' "
                f"has no lessons."
            )

        for lesson in chapter.lessons:

            if not lesson.title:

                raise ValueError(
                    "Lesson title is missing."
                )

            if not lesson.content:

                raise ValueError(
                    f"Lesson '{lesson.title}' "
                    f"has no content."
                )

            if not lesson.examples:

                raise ValueError(
                    f"Lesson '{lesson.title}' "
                    f"has no examples."
                )

            if len(lesson.quiz) != 3:

                raise ValueError(
                    f"Lesson '{lesson.title}' "
                    f"must contain exactly 3 quiz questions."
                )

            for question in lesson.quiz:

                if not question.question:

                    raise ValueError(
                        "Quiz question is empty."
                    )

                if len(question.options) != 4:

                    raise ValueError(
                        "Every quiz question must have "
                        "exactly 4 options."
                    )

                if len(
                    set(question.options)
                ) != 4:

                    raise ValueError(
                        "Quiz options must be unique."
                    )

                if question.answer not in question.options:

                    raise ValueError(
                        "Quiz answer does not match "
                        "one of the options."
                    )

    return True
