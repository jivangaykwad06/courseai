// ============================================================
// CourseAI - COURSE PAGE
// ============================================================

let currentCourse = null;
let currentChapterIndex = 0;
let currentLessonIndex = 0;

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        if (!requireLogin()) return;

        const params =
            new URLSearchParams(
                window.location.search
            );

        const courseId =
            params.get("id");

        if (!courseId) {

            showToast(
                "Course not found.",
                "error"
            );

            return;
        }

        await loadCourse(courseId);
    }
);

async function loadCourse(courseId) {

    try {

        const result =
            await apiGet(
                `/courses/${courseId}`
            );

        currentCourse =
            result.course ||
            result.data ||
            result;

        renderCourse();

    } catch (error) {

        console.error(
            "Course load error:",
            error
        );

        showToast(
            error.message ||
            "Unable to load course.",
            "error"
        );
    }
}

function renderCourse() {

    if (!currentCourse) return;

    setText(
        "courseTitle",
        currentCourse.title
    );

    setText(
        "courseDescription",
        currentCourse.description
    );

    setText(
        "courseCategory",
        currentCourse.category
    );

    setText(
        "courseDifficulty",
        currentCourse.difficulty
    );

    setText(
        "courseDuration",
        currentCourse.duration
    );

    const chapters =
        currentCourse.chapters ||
        [];

    const sidebar =
        document.getElementById(
            "chapterList"
        );

    if (!sidebar) return;

    sidebar.innerHTML =
        chapters.map(
            (chapter, index) => `
                <button
                    class="chapter-item ${
                        index === 0
                            ? "active"
                            : ""
                    }"
                    data-index="${index}">
                    <span>
                        Chapter ${
                            chapter.chapter_number ||
                            index + 1
                        }
                    </span>

                    <strong>
                        ${escapeHTML(
                            chapter.title
                        )}
                    </strong>
                </button>
            `
        ).join("");

    sidebar
        .querySelectorAll(
            ".chapter-item"
        )
        .forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    currentChapterIndex =
                        Number(
                            button.dataset.index
                        );

                    currentLessonIndex = 0;

                    sidebar
                        .querySelectorAll(
                            ".chapter-item"
                        )
                        .forEach(item =>
                            item.classList.remove(
                                "active"
                            )
                        );

                    button.classList.add(
                        "active"
                    );

                    renderLesson();
                }
            );
        });

    renderLesson();

    bindCourseButtons();
}

function renderLesson() {

    const chapters =
        currentCourse?.chapters ||
        [];

    const chapter =
        chapters[currentChapterIndex];

    if (!chapter) return;

    const lessons =
        chapter.lessons ||
        [];

    const lesson =
        lessons[currentLessonIndex];

    if (!lesson) {

        const lessonContainer =
            document.getElementById(
                "lessonContent"
            );

        if (lessonContainer) {

            lessonContainer.innerHTML = `
                <div class="empty-state">
                    <h3>No lessons available</h3>
                </div>
            `;
        }

        return;
    }

    setText(
        "chapterTitle",
        chapter.title
    );

    setText(
        "chapterDescription",
        chapter.description
    );

    setText(
        "lessonTitle",
        lesson.title
    );

    const content =
        document.getElementById(
            "lessonContent"
        );

    if (content) {

        content.innerHTML = `
            <div class="lesson-text">
                ${formatText(
                    lesson.content
                )}
            </div>

            ${
                lesson.examples
                    ? `
                    <section class="examples-section">
                        <h3>💡 Examples</h3>
                        <div>
                            ${formatText(
                                lesson.examples
                            )}
                        </div>
                    </section>
                    `
                    : ""
            }
        `;
    }

    renderQuiz(
        lesson.quiz || []
    );

    updateNavigation();
}

function renderQuiz(quiz) {

    const container =
        document.getElementById(
            "quizContainer"
        );

    if (!container) return;

    if (!Array.isArray(quiz) ||
        quiz.length === 0) {

        container.innerHTML = "";

        return;
    }

    container.innerHTML = `
        <section class="quiz-section">

            <h2>🧠 AI Generated Quiz</h2>

            ${quiz.map(
                (question, index) => {

                    const options =
                        question.options ||
                        [];

                    return `
                        <div
                            class="quiz-question"
                            data-question="${index}">

                            <h3>
                                ${index + 1}.
                                ${escapeHTML(
                                    question.question
                                )}
                            </h3>

                            <div class="quiz-options">

                                ${options.map(
                                    (option, optionIndex) => `
                                        <label>
                                            <input
                                                type="radio"
                                                name="quiz-${index}"
                                                value="${optionIndex}">
                                            <span>
                                                ${escapeHTML(
                                                    option
                                                )}
                                            </span>
                                        </label>
                                    `
                                ).join("")}

                            </div>

                        </div>
                    `;
                }
            ).join("")}

            <button
                id="submitQuizBtn"
                class="primary-btn">
                Submit Quiz
            </button>

            <div
                id="quizResult"
                class="quiz-result">
            </div>

        </section>
    `;

    document
        .getElementById(
            "submitQuizBtn"
        )
        ?.addEventListener(
            "click",
            () => submitQuiz(quiz)
        );
}

function submitQuiz(quiz) {

    let score = 0;

    quiz.forEach(
        (question, index) => {

            const selected =
                document.querySelector(
                    `input[name="quiz-${index}"]:checked`
                );

            if (!selected) return;

            const answer =
                String(
                    question.answer ??
                    question.correct_answer ??
                    ""
                ).trim();

            const selectedValue =
                selected.value;

            const options =
                question.options ||
                [];

            const selectedText =
                options[
                    Number(selectedValue)
                ];

            if (
                selectedText &&
                selectedText
                    .toLowerCase()
                    .trim() ===
                answer
                    .toLowerCase()
                    .trim()
            ) {
                score++;
            }
        }
    );

    const percentage =
        quiz.length
            ? Math.round(
                score /
                quiz.length *
                100
            )
            : 0;

    const result =
        document.getElementById(
            "quizResult"
        );

    if (result) {

        result.innerHTML = `
            <strong>
                Score: ${score}/${quiz.length}
                (${percentage}%)
            </strong>
        `;
    }
}

function bindCourseButtons() {

    document
        .getElementById(
            "markCompleteBtn"
        )
        ?.addEventListener(
            "click",
            markComplete
        );

    document
        .getElementById(
            "nextLessonBtn"
        )
        ?.addEventListener(
            "click",
            nextLesson
        );

    document
        .getElementById(
            "previousLessonBtn"
        )
        ?.addEventListener(
            "click",
            previousLesson
        );

    document
        .getElementById(
            "downloadPdfBtn"
        )
        ?.addEventListener(
            "click",
            downloadCoursePDF
        );
}

async function markComplete() {

    const chapter =
        currentCourse.chapters[
            currentChapterIndex
        ];

    const lesson =
        chapter.lessons[
            currentLessonIndex
        ];

    try {

        await apiPost(
            "/progress",
            {
                course_id:
                    currentCourse.id,

                lesson_id:
                    lesson.id,

                completed:
                    true
            }
        );

        showToast(
            "Lesson marked as complete!"
        );

    } catch (error) {

        showToast(
            error.message ||
            "Unable to save progress.",
            "error"
        );
    }
}

function nextLesson() {

    const chapter =
        currentCourse.chapters[
            currentChapterIndex
        ];

    if (
        currentLessonIndex <
        chapter.lessons.length - 1
    ) {

        currentLessonIndex++;

        renderLesson();

        return;
    }

    if (
        currentChapterIndex <
        currentCourse.chapters.length - 1
    ) {

        currentChapterIndex++;
        currentLessonIndex = 0;

        renderCourse();
    }
}

function previousLesson() {

    if (
        currentLessonIndex > 0
    ) {

        currentLessonIndex--;

        renderLesson();

        return;
    }

    if (
        currentChapterIndex > 0
    ) {

        currentChapterIndex--;

        const chapter =
            currentCourse.chapters[
                currentChapterIndex
            ];

        currentLessonIndex =
            Math.max(
                0,
                chapter.lessons.length - 1
            );

        renderCourse();
    }
}

function updateNavigation() {

    const previous =
        document.getElementById(
            "previousLessonBtn"
        );

    const next =
        document.getElementById(
            "nextLessonBtn"
        );

    if (previous) {

        previous.disabled =
            currentChapterIndex === 0 &&
            currentLessonIndex === 0;
    }

    const lastChapter =
        currentCourse.chapters.length - 1;

    const lastLesson =
        currentCourse
            .chapters[
                lastChapter
            ]
            .lessons.length - 1;

    if (next) {

        next.disabled =
            currentChapterIndex ===
                lastChapter &&
            currentLessonIndex ===
                lastLesson;
    }
}

async function downloadCoursePDF() {

    const button =
        document.getElementById(
            "downloadPdfBtn"
        );

    if (!currentCourse?.id) return;

    if (button) {

        button.disabled = true;
        button.textContent =
            "Preparing PDF...";
    }

    try {

        const token =
            getToken();

        const headers = {};

        if (token) {

            headers.Authorization =
                `Bearer ${token}`;
        }

        const response =
            await fetch(
                `${API_BASE}/courses/${currentCourse.id}/pdf`,
                {
                    headers,
                    credentials: "include"
                }
            );

        if (!response.ok) {

            throw new Error(
                "PDF generation failed."
            );
        }

        const blob =
            await response.blob();

        const url =
            URL.createObjectURL(blob);

        const link =
            document.createElement("a");

        link.href = url;

        link.download =
            `${sanitizeFilename(
                currentCourse.title
            )}.pdf`;

        document.body.appendChild(link);

        link.click();

        link.remove();

        URL.revokeObjectURL(url);

        showToast(
            "PDF downloaded successfully!"
        );

    } catch (error) {

        showToast(
            "Unable to generate PDF.",
            "error"
        );

    } finally {

        if (button) {

            button.disabled = false;
            button.textContent =
                "📄 Download Course PDF";
        }
    }
}

function formatText(text) {

    return escapeHTML(
        text || ""
    )
    .replace(/\n/g, "<br>");
}

function sanitizeFilename(name) {

    return String(name || "CourseAI_Course")
        .replace(/[<>:"/\\|?*]/g, "_")
        .trim();
}

function setText(id, value) {

    const element =
        document.getElementById(id);

    if (element) {
        element.textContent =
            value || "";
    }
}