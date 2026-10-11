// ============================================================
// CourseAI - PROFILE
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        if (!requireLogin()) return;

        const user =
            getStoredUser();

        if (user) {
            fillProfile(user);
        }

        try {

            const result =
                await apiGet(
                    "/auth/me"
                );

            const freshUser =
                result.user ||
                result.data ||
                result;

            fillProfile(
                freshUser
            );

        } catch (error) {

            console.log(
                "Using stored profile."
            );
        }
    }
);

function fillProfile(user) {

    if (!user) return;

    const mapping = {
        profileName:
            user.full_name ||
            user.name ||
            "",

        profileEmail:
            user.email ||
            "",

        profileRole:
            user.role ||
            "student",

        fullName:
            user.full_name ||
            user.name ||
            "",

        email:
            user.email ||
            ""
    };

    Object.keys(mapping)
        .forEach(id => {

            const element =
                document.getElementById(
                    id
                );

            if (element) {
                element.value !== undefined
                    ? element.value =
                        mapping[id]
                    : element.textContent =
                        mapping[id];
            }
        });
}