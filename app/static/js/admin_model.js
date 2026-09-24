const trainBtn = document.getElementById("train-btn");
const refreshBtn = document.getElementById("refresh-btn");
const trainMessage = document.getElementById("train-message");
const errorMessage = document.getElementById("error-message");

const modelStatusBadge = document.getElementById("model-status-badge");
const modelStatusText = document.getElementById("model-status-text");

const fields = {
    name: document.getElementById("model-name"),
    version: document.getElementById("model-version"),
    trained: document.getElementById("model-trained"),
    active: document.getElementById("model-active"),
};

function setModelInfo(data) {
    if (fields.name) fields.name.textContent = data.model || "-";
    if (fields.version) fields.version.textContent = data.version || "-";
    if (fields.trained) fields.trained.textContent = formatDate(data.trainedAt);
    
    if (fields.active) {
        if (data.isActive) {
            fields.active.innerHTML = `<span class="badge bg-success-subtle text-success border border-success px-2 py-1"><i class="bi bi-check-circle-fill me-1"></i> Đang hoạt động (Active)</span>`;
        } else {
            fields.active.innerHTML = `<span class="badge bg-secondary-subtle text-secondary border px-2 py-1">Không hoạt động</span>`;
        }
    }

    if (modelStatusText) {
        modelStatusText.textContent = data.isActive ? "Model Sẵn Sàng" : "Chưa Kích Hoạt";
    }
}

async function loadModelInfo() {
    hideError(errorMessage);
    if (trainMessage) trainMessage.classList.add("hidden");

    try {
        const data = await apiRequest("/api/model");
        setModelInfo(data);
    } catch (error) {
        setModelInfo({});
        showError(errorMessage, error.message);
    }
}

trainBtn.addEventListener("click", async () => {
    hideError(errorMessage);
    if (trainMessage) trainMessage.classList.add("hidden");

    trainBtn.disabled = true;
    if (refreshBtn) refreshBtn.disabled = true;
    const originalBtnHtml = trainBtn.innerHTML;
    trainBtn.innerHTML = `<i class="bi bi-arrow-repeat spin-icon"></i> <span>Đang huấn luyện mô hình...</span>`;
    
    if (modelStatusText) modelStatusText.textContent = "Đang xử lý...";

    try {
        const data = await apiRequest("/api/model/train", { method: "POST" });
        if (trainMessage) {
            trainMessage.innerHTML = `<i class="bi bi-check-circle-fill"></i> <span>${data.message || "Huấn luyện mô hình thành công!"}</span>`;
            trainMessage.classList.remove("hidden");
        }
        await loadModelInfo();
    } catch (error) {
        showError(errorMessage, error.message);
    } finally {
        trainBtn.disabled = false;
        if (refreshBtn) refreshBtn.disabled = false;
        trainBtn.innerHTML = originalBtnHtml;
    }
});

refreshBtn.addEventListener("click", async () => {
    const icon = refreshBtn.querySelector("i");
    if (icon) icon.classList.add("spin-icon");
    await loadModelInfo();
    if (icon) icon.classList.remove("spin-icon");
});

loadModelInfo();
