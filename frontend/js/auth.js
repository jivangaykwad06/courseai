// ============================================================
// CourseAI - AUTHENTICATION
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const loginForm =
            document.getElementById("loginForm");

        const signupForm =
            document.getElementById("signupForm");

        const logoutButtons =
            document.querySelectorAll(".logoutBtn");


        // ====================================================
        // LOGIN
        // ====================================================

        if (loginForm) {

            loginForm.addEventListener(
                "submit",
                async event => {

                    event.preventDefault();

                    const email =
                        document
                            .getElementById("email")
                            .value
                            .trim()
                            .toLowerCase();

                    const password =
                        document
                            .getElementById("password")
                            .value;

                    const remember =
                        document
                            .getElementById("rememberMe")
                            ?.checked || false;


                    // ------------------------------------------------
                    // EMAIL VALIDATION
                    // ------------------------------------------------

                    const emailPattern =
                        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


                    if (!email) {

                        showToast(
                            "Please enter your email address.",
                            "error"
                        );

                        return;
                    }


                    if (!emailPattern.test(email)) {

                        showToast(
                            "Please enter a valid email address.",
                            "error"
                        );

                        return;
                    }


                    if (!password) {

                        showToast(
                            "Please enter your password.",
                            "error"
                        );

                        return;
                    }


                    const button =
                        loginForm.querySelector(
                            "button[type='submit']"
                        );


                    button.disabled = true;

                    button.textContent =
                        "Logging in...";


                    try {

                        localStorage.setItem(
                            "courseAI_remember",
                            remember
                                ? "true"
                                : "false"
                        );


                        const result =
                            await apiPost(
                                "/auth/login",
                                {
                                    email,
                                    password
                                }
                            );


                        const user =
                            result.user ||
                            result.data?.user ||
                            result;


                        const token =
                            result.token ||
                            result.access_token ||
                            result.data?.token ||
                            "";


                        saveAuth(
                            user,
                            token
                        );


                        showToast(
                            "Login successful!"
                        );


                        setTimeout(
                            () => {

                                window.location.href =
                                    "dashboard.html";

                            },
                            600
                        );


                    } catch (error) {

                        console.error(
                            "Login error:",
                            error
                        );


                        showToast(
                            error.message ||
                            "Login failed.",
                            "error"
                        );


                        button.disabled =
                            false;

                        button.textContent =
                            "Login";
                    }

                }
            );
        }


        // ====================================================
        // SIGNUP
        // ====================================================

        if (signupForm) {

            signupForm.addEventListener(
                "submit",
                async event => {

                    event.preventDefault();


                    const fullName =
                        document
                            .getElementById("fullName")
                            .value
                            .trim();


                    const email =
                        document
                            .getElementById("email")
                            .value
                            .trim()
                            .toLowerCase();


                    const password =
                        document
                            .getElementById("password")
                            .value;


                    const confirmPassword =
                        document
                            .getElementById("confirmPassword")
                            .value;


                    const role =
                        document
                            .getElementById("role")
                            ?.value ||
                        "student";


                    const terms =
                        document
                            .getElementById("terms")
                            ?.checked;


                    // ------------------------------------------------
                    // EMAIL FORMAT VALIDATION
                    // ------------------------------------------------

                    const emailPattern =
                        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


                    // ------------------------------------------------
                    // REQUIRED FIELDS
                    // ------------------------------------------------

                    if (
                        !fullName ||
                        !email ||
                        !password ||
                        !confirmPassword
                    ) {

                        showToast(
                            "Please fill all required fields.",
                            "error"
                        );

                        return;
                    }


                    // ------------------------------------------------
                    // EMAIL VALIDATION
                    // ------------------------------------------------

                    if (!emailPattern.test(email)) {

                        showToast(
                            "Please enter a valid email address.",
                            "error"
                        );

                        return;
                    }


                    // ------------------------------------------------
                    // PASSWORD VALIDATION
                    // ------------------------------------------------

                    if (password.length < 8) {

                        showToast(
                            "Password must contain at least 8 characters.",
                            "error"
                        );

                        return;
                    }


                    // ------------------------------------------------
                    // CONFIRM PASSWORD
                    // ------------------------------------------------

                    if (
                        password !==
                        confirmPassword
                    ) {

                        showToast(
                            "Passwords do not match.",
                            "error"
                        );

                        return;
                    }


                    // ------------------------------------------------
                    // TERMS
                    // ------------------------------------------------

                    if (
                        document.getElementById(
                            "terms"
                        ) &&
                        !terms
                    ) {

                        showToast(
                            "Please accept the terms.",
                            "error"
                        );

                        return;
                    }


                    const button =
                        signupForm.querySelector(
                            "button[type='submit']"
                        );


                    button.disabled = true;

                    button.textContent =
                        "Creating account...";


                    try {

                        const result =
                            await apiPost(
                                "/auth/register",
                                {
                                    full_name:
                                        fullName,

                                    email,

                                    password,

                                    role
                                }
                            );


                        // --------------------------------------------
                        // REGISTRATION SUCCESS
                        // --------------------------------------------

                        if (result.success) {

                            showToast(
                                "Account created! Verification email sent to " +
                                email
                            );


                            // ----------------------------------------
                            // SHOW VERIFICATION MESSAGE
                            // ----------------------------------------

                            setTimeout(
                                () => {

                                    alert(
                                        "✅ Account created successfully!\n\n" +
                                        "A verification link has been sent to:\n" +
                                        email +
                                        "\n\n" +
                                        "Please open your email and click " +
                                        "\"Verify My Email\" before logging in."
                                    );


                                    window.location.href =
                                        "login.html";

                                },
                                800
                            );


                        } else {

                            throw new Error(
                                result.message ||
                                "Registration failed."
                            );
                        }


                    } catch (error) {

                        console.error(
                            "Registration error:",
                            error
                        );


                        showToast(
                            error.message ||
                            "Registration failed.",
                            "error"
                        );


                        button.disabled =
                            false;

                        button.textContent =
                            "Create Account";
                    }

                }
            );
        }


        // ====================================================
        // LOGOUT
        // ====================================================

        logoutButtons.forEach(
            button => {

                button.addEventListener(
                    "click",
                    async () => {

                        try {

                            await apiPost(
                                "/auth/logout",
                                {}
                            );

                        } catch (error) {

                            console.error(
                                "Logout error:",
                                error
                            );
                        }


                        clearAuth();


                        window.location.href =
                            "login.html";
                    }
                );

            }
        );

    }
);