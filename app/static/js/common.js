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
    return new Date(value).toLocaleString();
}

function showError(element, message) {
    if (!element) {
        return;
    }
    element.textContent = message;
    element.classList.remove("hidden");
}

function hideError(element) {
    if (!element) {
        return;
    }
    element.textContent = "";
    element.classList.add("hidden");
}
