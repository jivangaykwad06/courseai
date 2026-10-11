// ============================================================
// CourseAI - DASHBOARD
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        if (!requireLogin()) return;

        const user =
            getStoredUser();

        const nameElements =
            document.querySelectorAll(
                "[data-user-name]"
            );

        nameElements.forEach(element => {
            element.textContent =
                user?.full_name ||
                user?.name ||
                "Student";
        });

        await loadDashboard();
    }
);

async function loadDashboard() {

    try {

        const result =
            await apiGet("/courses");

        const courses =
            result.courses ||
            result.data ||
            result ||
            [];

        renderCourses(
            Array.isArray(courses)
                ? courses
                : []
        );

        await loadStatistics();

    } catch (error) {

        console.error(error);

        showToast(
            "Unable to load dashboard.",
            "error"
        );
    }
}

async function loadStatistics() {

    try {

        const result =
            await apiGet(
                "/courses"
            );

        const courses =
            result.courses ||
            result.data ||
            result ||
            [];

        const list =
            Array.isArray(courses)
                ? courses
                : [];

        let completed = 0;
        let inProgress = 0;
        let lessonsCompleted = 0;

        list.forEach(course => {

            const progress =
                Number(
                    course.progress ||
                    course.progress_percentage ||
                    0
                );

            if (progress >= 100) {
                completed++;
            } else if (progress > 0) {
                inProgress++;
            }

            lessonsCompleted +=
                Number(
                    course.lessons_completed ||
                    course.completed_lessons ||
                    0
                );
        });

        setText(
            "totalCourses",
            list.length
        );

        setText(
            "completedCourses",
            completed
        );

        setText(
            "inProgressCourses",
            inProgress
        );

        setText(
            "lessonsCompleted",
            lessonsCompleted
        );

    } catch (error) {

        console.error(
            "Statistics error:",
            error
        );
    }
}

function renderCourses(courses) {

    const container =
        document.getElementById(
            "coursesContainer"
        );

    if (!container) return;

    if (!courses.length) {

        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📚</div>
                <h3>No courses yet</h3>
                <p>Create your first AI-powered course.</p>
                <a href="create-course.html"
                   class="primary-btn">
                    + Create New Course
                </a>
            </div>
        `;

        return;
    }

    container.innerHTML =
        courses.map(course => {

            const progress =
                Math.min(
                    100,
                    Math.max(
                        0,
                        Number(
                            course.progress ||
                            course.progress_percentage ||
                            0
                        )
                    )
                );

            const id =
                course.id;

            return `
                <article class="course-card">

                    <div class="course-card-top">
                        <span class="course-category">
                            ${escapeHTML(
                                course.category ||
                                "General"
                            )}
                        </span>

                        <button
                            class="delete-course"
                            data-id="${id}"
                            title="Delete course">
                            🗑
                        </button>
                    </div>

                    <h3>
                        ${escapeHTML(
                            course.title
                        )}
                    </h3>

                    <p>
                        ${escapeHTML(
                            course.description ||
                            "AI generated course."
                        )}
                    </p>

                    <div class="course-meta">
                        <span>
                            🎯 ${escapeHTML(
                                course.difficulty ||
                                "Beginner"
                            )}
                        </span>

                        <span>
                            📖 ${
                                course.chapters_count ||
                                course.chapter_count ||
                                course.chapters ||
                                0
                            } Chapters
                        </span>
                    </div>

                    <div class="progress-info">
                        <span>Progress</span>
                        <strong>
                            ${progress}%
                        </strong>
                    </div>

                    <div class="progress-bar">
                        <div
                            class="progress-fill"
                            style="width:${progress}%">
                        </div>
                    </div>

                    <div class="course-actions">

                        <a
                            href="course.html?id=${id}"
                            class="primary-btn">
                            Open Course
                        </a>

                        <button
                            class="pdf-btn"
                            data-id="${id}">
                            📄 PDF
                        </button>

                    </div>

                </article>
            `;

        }).join("");

    bindCourseActions();
}

function bindCourseActions() {

    document
        .querySelectorAll(".delete-course")
        .forEach(button => {

            button.addEventListener(
                "click",
                async () => {

                    const id =
                        button.dataset.id;

                    if (
                        !confirm(
                            "Delete this course permanently?"
                        )
                    ) {
                        return;
                    }

                    try {

                        await apiDelete(
                            `/courses/${id}`
                        );

                        showToast(
                            "Course deleted."
                        );

                        await loadDashboard();

                    } catch (error) {

                        showToast(
                            error.message ||
                            "Unable to delete course.",
                            "error"
                        );
                    }
                }
            );
        });

    document
        .querySelectorAll(".pdf-btn")
        .forEach(button => {

            button.addEventListener(
                "click",
                () => downloadPDF(
                    button.dataset.id,
                    button
                )
            );
        });
}

async function downloadPDF(id, button) {

    const original =
        button.textContent;

    button.disabled = true;
    button.textContent =
        "Preparing...";

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
                `${API_BASE}/courses/${id}/pdf`,
                {
                    method: "GET",
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
            "CourseAI_Course.pdf";

        document.body.appendChild(link);

        link.click();

        link.remove();

        URL.revokeObjectURL(url);

        showToast(
            "PDF downloaded successfully."
        );

    } catch (error) {

        showToast(
            "Unable to generate PDF.",
            "error"
        );

    } finally {

        button.disabled = false;
        button.textContent =
            original;
    }
}

function setText(id, value) {

    const element =
        document.getElementById(id);

    if (element) {
        element.textContent =
            value;
    }
}