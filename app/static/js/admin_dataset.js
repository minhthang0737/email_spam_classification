const datasetForm = document.getElementById("dataset-form");
const datasetId = document.getElementById("dataset-id");
const datasetEmail = document.getElementById("dataset-email");
const datasetLabel = document.getElementById("dataset-label");
const datasetBody = document.getElementById("dataset-body");
const resetBtn = document.getElementById("dataset-reset-btn");
const errorMessage = document.getElementById("error-message");
const datasetTable = document.getElementById("dataset-table");
const datasetEmpty = document.getElementById("dataset-empty");

// Form State UI
const formTitle = document.getElementById("form-title");
const formModeBadge = document.getElementById("form-mode-badge");
const saveBtnText = document.getElementById("save-btn-text");

// Metrics
const statTotal = document.getElementById("dataset-stat-total");
const statSpam = document.getElementById("dataset-stat-spam");
const statSafe = document.getElementById("dataset-stat-safe");

// Search & Filter
const searchInput = document.getElementById("dataset-search-input");
const filterSelect = document.getElementById("dataset-filter-select");
const refreshBtn = document.getElementById("dataset-refresh-btn");

let allRecords = [];

function escapeHtml(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function resetForm() {
    datasetId.value = "";
    datasetEmail.value = "";
    datasetLabel.value = "SPAM";
    if (formTitle) formTitle.textContent = "Thêm Mẫu Mới";
    if (formModeBadge) {
        formModeBadge.textContent = "Thêm mới";
        formModeBadge.className = "badge bg-primary-subtle text-primary border";
    }
    if (saveBtnText) saveBtnText.textContent = "Thêm vào Dataset";
    hideError(errorMessage);
}

function updateStats(records) {
    const total = records.length;
    const spamCount = records.filter((r) => r.label === "SPAM").length;
    const safeCount = records.filter((r) => r.label === "NOT_SPAM").length;

    if (statTotal) statTotal.textContent = total;
    if (statSpam) statSpam.textContent = spamCount;
    if (statSafe) statSafe.textContent = safeCount;
}

function renderTableRows(records) {
    datasetBody.innerHTML = "";

    if (records.length === 0) {
        if (datasetEmpty) datasetEmpty.classList.remove("hidden");
        if (datasetTable) datasetTable.classList.add("hidden");
        return;
    }

    if (datasetEmpty) datasetEmpty.classList.add("hidden");
    if (datasetTable) datasetTable.classList.remove("hidden");

    records.forEach((record) => {
        const row = document.createElement("tr");
        const isSpam = record.label === "SPAM";

        const badgeHtml = isSpam
            ? `<span class="badge-pill-status spam"><i class="bi bi-shield-x"></i> SPAM</span>`
            : `<span class="badge-pill-status safe"><i class="bi bi-shield-check"></i> NOT_SPAM</span>`;

        row.innerHTML = `
            <td><span class="badge bg-light text-secondary border">#${record.id}</span></td>
            <td class="email-cell">${escapeHtml(record.email)}</td>
            <td>${badgeHtml}</td>
            <td class="text-secondary small"><i class="bi bi-calendar3 me-1"></i>${formatDate(record.createdAt)}</td>
            <td style="text-align: center;">
                <div class="d-inline-flex gap-1">
                    <button type="button" class="btn-secondary-custom table-action-btn" data-edit="${record.id}" title="Chỉnh sửa mẫu">
                        <i class="bi bi-pencil-fill"></i>
                    </button>
                    <button type="button" class="danger table-action-btn" data-delete="${record.id}" title="Xóa mẫu">
                        <i class="bi bi-trash3-fill"></i>
                    </button>
                </div>
            </td>
        `;
        datasetBody.appendChild(row);
    });

    // Attach Edit Listeners
    datasetBody.querySelectorAll("[data-edit]").forEach((button) => {
        button.addEventListener("click", () => {
            const id = button.getAttribute("data-edit");
            const record = allRecords.find((item) => String(item.id) === id);
            if (!record) return;

            datasetId.value = record.id;
            datasetEmail.value = record.email;
            datasetLabel.value = record.label;

            if (formTitle) formTitle.textContent = `Sửa Mẫu #${record.id}`;
            if (formModeBadge) {
                formModeBadge.textContent = `Đang sửa #${record.id}`;
                formModeBadge.className = "badge bg-warning-subtle text-warning-emphasis border border-warning";
            }
            if (saveBtnText) saveBtnText.textContent = "Lưu Thay Đổi";

            datasetEmail.focus();
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    });

    // Attach Delete Listeners
    datasetBody.querySelectorAll("[data-delete]").forEach((button) => {
        button.addEventListener("click", async () => {
            const id = button.getAttribute("data-delete");
            if (!confirm(`Bạn có chắc muốn xóa mẫu huấn luyện #${id}?`)) {
                return;
            }
            try {
                button.disabled = true;
                await apiRequest(`/api/dataset/${id}`, { method: "DELETE" });
                await loadDataset();
            } catch (error) {
                showError(errorMessage, error.message);
                button.disabled = false;
            }
        });
    });
}

function applyFilters() {
    const query = (searchInput ? searchInput.value : "").trim().toLowerCase();
    const filter = filterSelect ? filterSelect.value : "ALL";

    const filtered = allRecords.filter((record) => {
        const matchesQuery = !query || (record.email && record.email.toLowerCase().includes(query));
        const matchesFilter = filter === "ALL" || record.label === filter;
        return matchesQuery && matchesFilter;
    });

    renderTableRows(filtered);
}

async function loadDataset() {
    hideError(errorMessage);

    try {
        const data = await apiRequest("/api/dataset");
        allRecords = data.data || [];
        updateStats(allRecords);
        applyFilters();
    } catch (error) {
        showError(errorMessage, error.message);
    }
}

datasetForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    hideError(errorMessage);

    const payload = {
        email: datasetEmail.value.trim(),
        label: datasetLabel.value,
    };

    const submitBtn = document.getElementById("dataset-save-btn");
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i class="bi bi-arrow-repeat spin-icon"></i> <span>Đang lưu...</span>`;

    try {
        if (datasetId.value) {
            await apiRequest(`/api/dataset/${datasetId.value}`, {
                method: "PUT",
                body: JSON.stringify(payload),
            });
        } else {
            await apiRequest("/api/dataset", {
                method: "POST",
                body: JSON.stringify(payload),
            });
        }
        resetForm();
        await loadDataset();
    } catch (error) {
        showError(errorMessage, error.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
});

resetBtn.addEventListener("click", resetForm);

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
        await loadDataset();
        if (icon) icon.classList.remove("spin-icon");
    });
}

loadDataset();
