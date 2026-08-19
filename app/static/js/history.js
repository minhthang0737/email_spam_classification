const historyBody = document.getElementById("history-body");
const historyEmpty = document.getElementById("history-empty");
const errorMessage = document.getElementById("error-message");

async function loadHistory() {
    hideError(errorMessage);
    historyBody.innerHTML = "";

    try {
        const data = await apiRequest("/api/classifications");
        const records = data.data || [];

        if (records.length === 0) {
            historyEmpty.classList.remove("hidden");
            return;
        }

        historyEmpty.classList.add("hidden");

        records.forEach((record) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${record.id}</td>
                <td class="email-cell">${record.email}</td>
                <td class="${record.result === "SPAM" ? "badge-spam" : "badge-not-spam"}">${record.result}</td>
                <td>${formatConfidence(record.confidence)}</td>
                <td>${formatDate(record.createdAt)}</td>
                <td><button type="button" data-id="${record.id}">Xóa</button></td>
            `;
            historyBody.appendChild(row);
        });

        historyBody.querySelectorAll("button").forEach((button) => {
            button.addEventListener("click", async () => {
                const id = button.getAttribute("data-id");
                try {
                    await apiRequest(`/api/classifications/${id}`, { method: "DELETE" });
                    await loadHistory();
                } catch (error) {
                    showError(errorMessage, error.message);
                }
            });
        });
    } catch (error) {
        showError(errorMessage, error.message);
    }
}

loadHistory();
