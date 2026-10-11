// ============================================================
// CourseAI - API CORE
// ============================================================

const API_BASE = "/api";

function getToken() {
    return localStorage.getItem("courseAI_token") ||
           sessionStorage.getItem("courseAI_token") ||
           "";
}

function getStoredUser() {
    const data =
        localStorage.getItem("courseAI_user") ||
        sessionStorage.getItem("courseAI_user");

    if (!data) return null;

    try {
        return JSON.parse(data);
    } catch {
        return null;
    }
}

function saveAuth(user, token = "") {
    const remember =
        localStorage.getItem("courseAI_remember") === "true";

    const storage =
        remember ? localStorage : sessionStorage;

    storage.setItem(
        "courseAI_user",
        JSON.stringify(user)
    );

    if (token) {
        storage.setItem(
            "courseAI_token",
            token
        );
    }
}

function clearAuth() {
    localStorage.removeItem("courseAI_user");
    localStorage.removeItem("courseAI_token");
    localStorage.removeItem("courseAI_remember");

    sessionStorage.removeItem("courseAI_user");
    sessionStorage.removeItem("courseAI_token");
}

async function apiFetch(endpoint, options = {}) {

    const headers = {
        ...(options.headers || {})
    };

    if (
        options.body &&
        !(options.body instanceof FormData) &&
        !headers["Content-Type"]
    ) {
        headers["Content-Type"] = "application/json";
    }

    const token = getToken();

    if (token) {
        headers["Authorization"] =
            `Bearer ${token}`;
    }

    const response = await fetch(
        API_BASE + endpoint,
        {
            ...options,
            headers,
            credentials: "include"
        }
    );

    let data = null;

    const contentType =
        response.headers.get("content-type") || "";

    if (contentType.includes("application/json")) {
        data = await response.json();
    } else {
        const text = await response.text();

        data = {
            success: response.ok,
            message: text
        };
    }

    if (!response.ok) {

        if (response.status === 401) {
            clearAuth();
        }

        throw new Error(
            data.message ||
            data.error ||
            "Request failed."
        );
    }

    return data;
}

async function apiGet(endpoint) {
    return apiFetch(endpoint, {
        method: "GET"
    });
}

async function apiPost(endpoint, body) {
    return apiFetch(endpoint, {
        method: "POST",
        body: JSON.stringify(body)
    });
}

async function apiPut(endpoint, body) {
    return apiFetch(endpoint, {
        method: "PUT",
        body: JSON.stringify(body)
    });
}

async function apiDelete(endpoint) {
    return apiFetch(endpoint, {
        method: "DELETE"
    });
}

async function getCurrentUser() {
    try {
        return await apiGet("/auth/me");
    } catch {
        return null;
    }
}

function requireLogin() {

    const user = getStoredUser();

    if (!user) {
        window.location.href = "login.html";
        return false;
    }

    return true;
}

function showToast(message, type = "success") {

    let toast =
        document.getElementById("toast");

    if (!toast) {

        toast = document.createElement("div");

        toast.id = "toast";

        document.body.appendChild(toast);
    }

    toast.className =
        `toast toast-${type}`;

    toast.textContent = message;

    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3500);
}

function escapeHTML(value) {

    if (value === null ||
        value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}