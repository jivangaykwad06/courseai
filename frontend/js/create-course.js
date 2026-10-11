// ============================================================
// CourseAI - CREATE COURSE
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        if (!requireLogin()) return;

        const form =
            document.getElementById(
                "courseForm"
            );

        if (!form) return;

        form.addEventListener(
            "submit",
            generateCourse
        );
    }
);

async function generateCourse(event) {

    event.preventDefault();

    const title =
        document.getElementById(
            "courseTitle"
        ).value.trim();

    const category =
        document.getElementById(
            "category"
        ).value.trim();

    const difficulty =
        document.getElementById(
            "difficulty"
        ).value;

    const duration =
        document.getElementById(
            "duration"
        ).value.trim();

    const chapters =
        Number(
            document.getElementById(
                "chapters"
            ).value
        );

    const requirements =
        document.getElementById(
            "requirements"
        ).value.trim();

    if (
        !title ||
        !category ||
        !difficulty ||
        !duration ||
        !chapters
    ) {

        showToast(
            "Please fill all required fields.",
            "error"
        );

        return;
    }

    const button =
        document.getElementById(
            "generateBtn"
        );

    const loading =
        document.getElementById(
            "generationLoading"
        );

    button.disabled = true;

    button.textContent =
        "🤖 Generating with AI...";

    if (loading) {
        loading.classList.add("show");
    }

    try {

        const result =
            await apiPost(
                "/ai/generate-course",
                {
                    title,
                    course_title: title,
                    category,
                    difficulty,
                    duration,
                    chapters,
                    number_of_chapters:
                        chapters,
                    requirements,
                    additional_requirements:
                        requirements
                }
            );

        const course =
            result.course ||
            result.data?.course;

        const courseId =
            result.course_id ||
            result.data?.course_id ||
            course?.id;

        if (!courseId) {

            throw new Error(
                "AI generated the course but no course ID was returned."
            );
        }

        showToast(
            "AI course generated successfully!"
        );

        setTimeout(() => {

            window.location.href =
                `course.html?id=${courseId}`;

        }, 700);

    } catch (error) {

        console.error(
            "AI generation error:",
            error
        );

        showToast(
            error.message ||
            "Course generation failed.",
            "error"
        );

        button.disabled = false;

        button.textContent =
            "✨ Generate Course with AI";

    } finally {

        if (loading) {
            loading.classList.remove(
                "show"
            );
        }
    }
}