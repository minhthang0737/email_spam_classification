const historyBody = document.getElementById("history-body");
const historyEmpty = document.getElementById("history-empty");
const errorMessage = document.getElementById("error-message");
const historyTable = document.getElementById("history-table");

// Metric Stat Elements
const statTotal = document.getElementById("history-stat-total");
const statSpam = document.getElementById("history-stat-spam");
const statSafe = document.getElementById("history-stat-safe");
const statRate = document.getElementById("history-stat-rate");

// Toolbar Elements
const searchInput = document.getElementById("history-search-input");
const filterSelect = document.getElementById("history-filter-select");
const refreshBtn = document.getElementById("history-refresh-btn");

let allRecords = [];

function escapeHtml(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function updateStats(records) {
    const total = records.length;
    const spamCount = records.filter((r) => r.result === "SPAM").length;
    const safeCount = records.filter((r) => r.result === "NOT_SPAM").length;
    const rate = total > 0 ? ((spamCount / total) * 100).toFixed(1) : 0;

    if (statTotal) statTotal.textContent = total;
    if (statSpam) statSpam.textContent = spamCount;
    if (statSafe) statSafe.textContent = safeCount;
    if (statRate) statRate.textContent = `${rate}%`;
}

function renderTableRows(records) {
    historyBody.innerHTML = "";

    if (records.length === 0) {
        historyEmpty.classList.remove("hidden");
        if (historyTable) historyTable.classList.add("hidden");
        return;
    }

    historyEmpty.classList.add("hidden");
    if (historyTable) historyTable.classList.remove("hidden");

    records.forEach((record) => {
        const row = document.createElement("tr");
        const isSpam = record.result === "SPAM";
        const percentVal = record.confidence != null ? Math.round(record.confidence * 100) : null;

        const badgeHtml = isSpam
            ? `<span class="badge-pill-status spam"><i class="bi bi-shield-x"></i> SPAM</span>`
            : `<span class="badge-pill-status safe"><i class="bi bi-shield-check"></i> NOT_SPAM</span>`;

        const confidenceBarHtml = percentVal != null
            ? `<div>
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="small font-weight-bold">${percentVal}%</span>
                </div>
                <div class="progress" style="height: 6px; background-color: #e2e8f0; border-radius: 99px;">
                    <div class="progress-bar ${isSpam ? 'bg-danger' : 'bg-success'}" style="width: ${percentVal}%; border-radius: 99px;"></div>
                </div>
               </div>`
            : "-";

        row.innerHTML = `
            <td><span class="badge bg-light text-secondary border">#${record.id}</span></td>
            <td class="email-cell">${escapeHtml(record.email)}</td>
            <td>${badgeHtml}</td>
            <td>${confidenceBarHtml}</td>
            <td class="text-secondary small"><i class="bi bi-calendar3 me-1"></i>${formatDate(record.createdAt)}</td>
            <td>
                <div class="d-flex align-items-center">
                    <select class="form-control form-control-sm feedback-label" aria-label="Nhãn đúng cho email ${record.id}">
                        <option value="SPAM" ${isSpam ? "selected" : ""}>SPAM</option>
                        <option value="NOT_SPAM" ${!isSpam ? "selected" : ""}>NOT_SPAM</option>
                    </select>
                    <button type="button" class="btn btn-sm btn-outline-primary feedback-save ml-2" data-id="${record.id}">Lưu nhãn</button>
                </div>
                <small class="feedback-status text-muted"></small>
            </td>
            <td style="text-align: center;">
                <button type="button" class="danger table-action-btn" data-id="${record.id}" title="Xóa bản ghi này">
                    <i class="bi bi-trash3-fill"></i>
                </button>
            </td>
        `;
        historyBody.appendChild(row);
    });

    // Attach delete listeners
    historyBody.querySelectorAll("button.table-action-btn[data-id]").forEach((button) => {
        button.addEventListener("click", async () => {
            const id = button.getAttribute("data-id");
            if (!confirm(`Bạn có chắc chắn muốn xóa bản ghi lịch sử #${id}?`)) {
                return;
            }
            try {
                button.disabled = true;
                await apiRequest(`/api/classifications/${id}`, { method: "DELETE" });
                await loadHistory();
            } catch (error) {
                showError(errorMessage, error.message);
                button.disabled = false;
            }
        });
    });

    historyBody.querySelectorAll("button.feedback-save").forEach((button) => {
        button.addEventListener("click", async () => {
            const row = button.closest("tr");
            const label = row.querySelector(".feedback-label").value;
            const status = row.querySelector(".feedback-status");
            button.disabled = true;
            try {
                const result = await apiRequest(`/api/classifications/${button.dataset.id}/feedback`, {
                    method: "POST", body: JSON.stringify({ label }),
                });
                status.textContent = result.action === "unchanged" ? "Đã có nhãn này" : result.action === "updated" ? "Đã sửa nhãn trong dataset" : "Đã thêm vào dataset";
                status.className = "feedback-status text-success";
            } catch (error) {
                showError(errorMessage, error.message);
            } finally { button.disabled = false; }
        });
    });

}

function applyFilters() {
    const query = (searchInput ? searchInput.value : "").trim().toLowerCase();
    const filter = filterSelect ? filterSelect.value : "ALL";

    const filtered = allRecords.filter((record) => {
        const matchesQuery = !query || (record.email && record.email.toLowerCase().includes(query));
        const matchesFilter = filter === "ALL" || record.result === filter;
        return matchesQuery && matchesFilter;
    });

    renderTableRows(filtered);
}

async function loadHistory() {
    hideError(errorMessage);

    try {
        const data = await apiRequest("/api/classifications");
        allRecords = data.data || [];
        updateStats(allRecords);
        applyFilters();
    } catch (error) {
        showError(errorMessage, error.message);
    }
}

if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
}

if (filterSelect) {
    filterSelect.addEventListener("change", applyFilters);
}

if (refreshBtn) {
    refreshBtn.addEventListener("click", async () => {
        const icon = refreshBtn.querySelector("i");
        if (icon) icon.classList.add("spin-icon");
        await loadHistory();
        if (icon) icon.classList.remove("spin-icon");
    });
}

loadHistory();
