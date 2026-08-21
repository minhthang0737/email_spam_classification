const emailInput = document.getElementById("email-input");
const predictBtn = document.getElementById("predict-btn");
const clearBtn = document.getElementById("clear-btn");
const resultPanel = document.getElementById("result-panel");
const resultLabel = document.getElementById("result-label");
const resultConfidence = document.getElementById("result-confidence");
const errorMessage = document.getElementById("error-message");

predictBtn.addEventListener("click", async () => {
    hideError(errorMessage);
    resultPanel.classList.add("hidden");

    const email = emailInput.value.trim();
    if (!email) {
        showError(errorMessage, "Email content cannot be empty.");
        return;
    }

    try {
        const data = await apiRequest("/api/predict", {
            method: "POST",
            body: JSON.stringify({ email }),
        });

        resultLabel.textContent = data.result;
        resultLabel.className = data.result === "SPAM" ? "badge-spam" : "badge-not-spam";
        resultConfidence.textContent = formatConfidence(data.confidence);
        resultPanel.classList.remove("hidden");
    } catch (error) {
        showError(errorMessage, error.message);
    }
});

clearBtn.addEventListener("click", () => {
    emailInput.value = "";
    resultPanel.classList.add("hidden");
    hideError(errorMessage);
});
