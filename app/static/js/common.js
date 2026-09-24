async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        ...options,
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        const message = data.message || `Request failed (${response.status})`;
        throw new Error(message);
    }

    return data;
}

function formatConfidence(value) {
    if (value === null || value === undefined) {
        return "-";
    }
    return `${(value * 100).toFixed(1)}%`;
}

function formatDate(value) {
    if (!value) {
        return "-";
    }
    const d = new Date(value);
    if (isNaN(d.getTime())) {
        return value;
    }
    return d.toLocaleString("vi-VN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
    });
}

function showError(element, message) {
    if (!element) {
        return;
    }
    element.innerHTML = `<i class="bi bi-exclamation-triangle-fill"></i> <span>${message}</span>`;
    element.classList.remove("hidden");
}

function hideError(element) {
    if (!element) {
        return;
    }
    element.innerHTML = "";
    element.classList.add("hidden");
}
