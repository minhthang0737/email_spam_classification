const emailInput = document.getElementById("email-input");
const predictBtn = document.getElementById("predict-btn");
const clearBtn = document.getElementById("clear-btn");
const pasteBtn = document.getElementById("paste-btn");
const resultPanel = document.getElementById("result-panel");
const resultLabel = document.getElementById("result-label");
const resultConfidence = document.getElementById("result-confidence");
const errorMessage = document.getElementById("error-message");

// Additional UI elements
const wordCountEl = document.getElementById("word-count");
const charCountEl = document.getElementById("char-count");
const resultBanner = document.getElementById("result-banner");
const resultIcon = document.getElementById("result-icon");
const resultSubDesc = document.getElementById("result-sub-desc");
const resultProgressBar = document.getElementById("result-progress-bar");
const resultRiskLevel = document.getElementById("result-risk-level");
const resultRecommendation = document.getElementById("result-recommendation");
const resultTimestamp = document.getElementById("result-timestamp");
const predictBtnText = document.getElementById("predict-btn-text");

// Sample Email Text Library
const SAMPLE_EMAILS = {
    "spam-lottery": "CONGRATULATIONS! You have been selected as the winner of $1,000,000 in our international online cash lottery! Claim your urgent prize reward right now by clicking the link before it expires.",
    "spam-bank": "SECURITY WARNING: Urgent action required on your bank account. We noticed unauthorized login attempts. Click here immediately to verify your account credentials and password or your funds will be locked.",
    "safe-meeting": "Hi team, please find attached the agenda for tomorrow's sprint review meeting at 9:30 AM in Conference Room 3. Please review your task progress and sprint goals beforehand.",
    "safe-study": "Chào thầy cô và các bạn, nhóm em xin gửi tài liệu báo cáo đồ án kết thúc học phần và slide thuyết trình theo yêu cầu. Nhóm rất mong nhận được những nhận xét quý báu từ thầy.",
};

function updateCounters() {
    if (!emailInput) return;
    const text = emailInput.value.trim();
    const charCount = emailInput.value.length;
    const words = text ? text.split(/\s+/).filter(Boolean) : [];
    if (charCountEl) charCountEl.textContent = charCount;
    if (wordCountEl) wordCountEl.textContent = words.length;
}

if (emailInput) {
    emailInput.addEventListener("input", updateCounters);
}

// Paste button handler
if (pasteBtn && emailInput) {
    pasteBtn.addEventListener("click", async () => {
        try {
            const text = await navigator.clipboard.readText();
            if (text) {
                emailInput.value = text;
                updateCounters();
                emailInput.focus();
            }
        } catch {
            showError(errorMessage, "Không thể truy cập clipboard. Vui lòng dán trực tiếp (Ctrl+V).");
        }
    });
}

// Quick Sample Buttons
document.querySelectorAll(".sample-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
        const sampleKey = chip.getAttribute("data-sample");
        if (SAMPLE_EMAILS[sampleKey] && emailInput) {
            emailInput.value = SAMPLE_EMAILS[sampleKey];
            updateCounters();
            emailInput.focus();
            hideError(errorMessage);
        }
    });
});

// Predict Button Handler
predictBtn.addEventListener("click", async () => {
    hideError(errorMessage);
    resultPanel.classList.add("hidden");

    const email = emailInput.value.trim();
    if (!email) {
        showError(errorMessage, "Vui lòng nhập hoặc dán nội dung email cần kiểm tra.");
        return;
    }

    // Set loading state
    predictBtn.disabled = true;
    const originalBtnHtml = predictBtn.innerHTML;
    predictBtn.innerHTML = `<i class="bi bi-arrow-repeat spin-icon"></i> <span>Đang phân tích...</span>`;

    try {
        const data = await apiRequest("/api/predict", {
            method: "POST",
            body: JSON.stringify({ email }),
        });

        // Update core label & classes
        resultLabel.textContent = data.result;
        resultLabel.className = data.result === "SPAM" ? "badge-spam" : "badge-not-spam";
        resultConfidence.textContent = formatConfidence(data.confidence);

        // Update enhanced UI visuals
        const isSpam = data.result === "SPAM";
        const percent = Math.min(Math.max((data.confidence * 100), 0), 100);

        if (resultBanner) {
            resultBanner.className = `result-banner ${isSpam ? "is-spam" : "is-not-spam"}`;
        }

        if (resultIcon) {
            resultIcon.className = isSpam
                ? "bi bi-exclamation-octagon-fill text-danger"
                : "bi bi-shield-check text-success";
        }

        if (resultSubDesc) {
            resultSubDesc.textContent = isSpam
                ? "Cảnh báo nguy hiểm: Bức thư này chứa nhiều đặc điểm của thư rác hoặc lừa đảo tài chính."
                : "Thư an toàn: Nội dung đáng tin cậy, không phát hiện dấu hiệu lừa đảo nguy hiểm.";
        }

        if (resultProgressBar) {
            resultProgressBar.className = `progress-fill-custom ${isSpam ? "is-spam" : "is-safe"}`;
            resultProgressBar.style.width = `${percent.toFixed(1)}%`;
        }

        if (resultRiskLevel) {
            resultRiskLevel.innerHTML = isSpam
                ? `<span class="badge-spam"><i class="bi bi-shield-exclamation"></i> Nguy cơ cao</span>`
                : `<span class="badge-not-spam"><i class="bi bi-shield-check"></i> An toàn</span>`;
        }

        if (resultRecommendation) {
            resultRecommendation.textContent = isSpam
                ? "Không nhấp vào link, đưa vào thư rác"
                : "Có thể tin tưởng & xử lý bình thường";
        }

        if (resultTimestamp) {
            resultTimestamp.textContent = new Date().toLocaleTimeString("vi-VN");
        }

        resultPanel.classList.remove("hidden");
        resultPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } catch (error) {
        showError(errorMessage, error.message);
    } finally {
        predictBtn.disabled = false;
        predictBtn.innerHTML = originalBtnHtml;
    }
});

// Clear Button Handler
clearBtn.addEventListener("click", () => {
    emailInput.value = "";
    resultPanel.classList.add("hidden");
    hideError(errorMessage);
    updateCounters();
});
