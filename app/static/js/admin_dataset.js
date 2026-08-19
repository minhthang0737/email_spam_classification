const datasetForm = document.getElementById("dataset-form");
const datasetId = document.getElementById("dataset-id");
const datasetEmail = document.getElementById("dataset-email");
const datasetLabel = document.getElementById("dataset-label");
const datasetBody = document.getElementById("dataset-body");
const resetBtn = document.getElementById("dataset-reset-btn");
const errorMessage = document.getElementById("error-message");

function resetForm() {
    datasetId.value = "";
    datasetEmail.value = "";
    datasetLabel.value = "SPAM";
}

async function loadDataset() {
    hideError(errorMessage);
    datasetBody.innerHTML = "";

    try {
        const data = await apiRequest("/api/dataset");
        const records = data.data || [];

        records.forEach((record) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${record.id}</td>
                <td class="email-cell">${record.email}</td>
                <td>${record.label}</td>
                <td>${formatDate(record.createdAt)}</td>
                <td>
                    <button type="button" data-edit="${record.id}">Sửa</button>
                    <button type="button" data-delete="${record.id}">Xóa</button>
                </td>
            `;
            datasetBody.appendChild(row);
        });

        datasetBody.querySelectorAll("[data-edit]").forEach((button) => {
            button.addEventListener("click", () => {
                const id = button.getAttribute("data-edit");
                const record = records.find((item) => String(item.id) === id);
                if (!record) {
                    return;
                }
                datasetId.value = record.id;
                datasetEmail.value = record.email;
                datasetLabel.value = record.label;
            });
        });

        datasetBody.querySelectorAll("[data-delete]").forEach((button) => {
            button.addEventListener("click", async () => {
                const id = button.getAttribute("data-delete");
                try {
                    await apiRequest(`/api/dataset/${id}`, { method: "DELETE" });
                    await loadDataset();
                } catch (error) {
                    showError(errorMessage, error.message);
                }
            });
        });
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
    }
});

resetBtn.addEventListener("click", resetForm);

loadDataset();
