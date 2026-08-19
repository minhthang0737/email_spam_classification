const trainBtn = document.getElementById("train-btn");
const refreshBtn = document.getElementById("refresh-btn");
const trainMessage = document.getElementById("train-message");
const errorMessage = document.getElementById("error-message");

const fields = {
    name: document.getElementById("model-name"),
    version: document.getElementById("model-version"),
    accuracy: document.getElementById("model-accuracy"),
    precision: document.getElementById("model-precision"),
    recall: document.getElementById("model-recall"),
    f1: document.getElementById("model-f1"),
    trained: document.getElementById("model-trained"),
    active: document.getElementById("model-active"),
};

function setModelInfo(data) {
    fields.name.textContent = data.model || "-";
    fields.version.textContent = data.version || "-";
    fields.accuracy.textContent = data.accuracy ?? "-";
    fields.precision.textContent = data.precision ?? "-";
    fields.recall.textContent = data.recall ?? "-";
    fields.f1.textContent = data.f1Score ?? "-";
    fields.trained.textContent = formatDate(data.trainedAt);
    fields.active.textContent = data.isActive ? "Yes" : "No";
}

async function loadModelInfo() {
    hideError(errorMessage);
    trainMessage.classList.add("hidden");

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
    trainMessage.classList.add("hidden");

    try {
        const data = await apiRequest("/api/model/train", { method: "POST" });
        trainMessage.textContent = `${data.message} (accuracy: ${data.accuracy})`;
        trainMessage.classList.remove("hidden");
        await loadModelInfo();
    } catch (error) {
        showError(errorMessage, error.message);
    }
});

refreshBtn.addEventListener("click", loadModelInfo);

loadModelInfo();
