const ipError = document.getElementById("ip-admin-error");
const ipBody = document.getElementById("ip-block-body");
const domainError = document.getElementById("domain-admin-error");
const domainBody = document.getElementById("domain-block-body");
const resultTable = document.getElementById("ip-results");
const domainResultTable = document.getElementById("domain-results");
const ipMessage = document.getElementById("ip-check-message");

async function loadBlockedIps() {
    ipError.classList.add("hidden");
    const data = await apiRequest("/api/ip/blocklist");
    ipBody.replaceChildren();
    data.data.forEach((item) => {
        const row = document.createElement("tr");
        [item.ip, item.reason, formatDate(item.createdAt)].forEach((text) => {
            const cell = document.createElement("td"); cell.textContent = text; row.appendChild(cell);
        });
        const action = document.createElement("td");
        const edit = document.createElement("button"); edit.className = "btn btn-sm btn-outline-secondary mr-1"; edit.textContent = "Sửa lý do";
        edit.addEventListener("click", async () => {
            const reason = prompt("Lý do chặn IP:", item.reason);
            if (reason === null) return;
            try { await apiRequest(`/api/ip/blocklist/${item.id}`, {method:"PUT", body:JSON.stringify({reason})}); await loadBlockedIps(); }
            catch (error) { ipError.textContent = error.message; ipError.classList.remove("hidden"); }
        });
        const del = document.createElement("button"); del.className = "btn btn-sm btn-outline-danger"; del.textContent = "Xóa";
        del.addEventListener("click", async () => {
            if (!confirm(`Xóa ${item.ip} khỏi danh sách chặn?`)) return;
            try { await apiRequest(`/api/ip/blocklist/${item.id}`, {method:"DELETE"}); await loadBlockedIps(); }
            catch (error) { ipError.textContent = error.message; ipError.classList.remove("hidden"); }
        });
        action.append(edit, del); row.appendChild(action); ipBody.appendChild(row);
    });
}

async function loadBlockedDomains() {
    domainError.classList.add("hidden");
    const data = await apiRequest("/api/ip/domain-blocklist");
    domainBody.replaceChildren();
    data.data.forEach((item) => {
        const row = document.createElement("tr");
        [item.domain, item.reason, formatDate(item.createdAt)].forEach((text) => {
            const cell = document.createElement("td"); cell.textContent = text; row.appendChild(cell);
        });
        const action = document.createElement("td");
        const edit = document.createElement("button"); edit.className = "btn btn-sm btn-outline-secondary mr-1"; edit.textContent = "Sửa";
        edit.addEventListener("click", async () => {
            const domain = prompt("Domain cần chặn:", item.domain);
            if (domain === null) return;
            const reason = prompt("Lý do chặn:", item.reason);
            if (reason === null) return;
            try { await apiRequest(`/api/ip/domain-blocklist/${item.id}`, {method:"PUT", body:JSON.stringify({domain, reason})}); await loadBlockedDomains(); }
            catch (error) { domainError.textContent = error.message; domainError.classList.remove("hidden"); }
        });
        const del = document.createElement("button"); del.className = "btn btn-sm btn-outline-danger"; del.textContent = "Xóa";
        del.addEventListener("click", async () => {
            if (!confirm(`Bỏ chặn ${item.domain}?`)) return;
            try { await apiRequest(`/api/ip/domain-blocklist/${item.id}`, {method:"DELETE"}); await loadBlockedDomains(); }
            catch (error) { domainError.textContent = error.message; domainError.classList.remove("hidden"); }
        });
        action.append(edit, del); row.appendChild(action); domainBody.appendChild(row);
    });
}

document.getElementById("ip-check-btn").addEventListener("click", async () => {
    ipMessage.textContent = "Đang kiểm tra...";
    try {
        const data = await apiRequest("/api/ip/check", {method:"POST", body:JSON.stringify({text:document.getElementById("ip-check-text").value})});
        const body = resultTable.querySelector("tbody"); body.replaceChildren();
        data.data.forEach((item) => {
            const row = document.createElement("tr");
            [item.ip, `IPv${item.version}`, item.scope, item.blocked ? "CÓ" : "Không", item.reason || "—"].forEach((value) => {const td=document.createElement("td");td.textContent=value;row.appendChild(td);});
            body.appendChild(row);
        });
        resultTable.classList.toggle("hidden", !data.count);
        const domainBody = domainResultTable.querySelector("tbody"); domainBody.replaceChildren();
        data.domains.forEach((item) => {
            const row = document.createElement("tr");
            [item.domain, item.blocked ? "CÓ" : "Không", item.reason || "—"].forEach((value) => {const td=document.createElement("td");td.textContent=value;row.appendChild(td);});
            domainBody.appendChild(row);
        });
        domainResultTable.classList.toggle("hidden", !data.domainCount);
        ipMessage.textContent = `Tìm thấy ${data.count} IP và ${data.domainCount} domain.`;
    } catch (error) { ipMessage.textContent = error.message; }
});

document.getElementById("ip-block-form").addEventListener("submit", async (event) => {
    event.preventDefault(); ipError.classList.add("hidden");
    try {
        await apiRequest("/api/ip/blocklist", {method:"POST", body:JSON.stringify({ip:document.getElementById("blocked-ip").value,reason:document.getElementById("blocked-reason").value})});
        event.target.reset(); await loadBlockedIps();
    } catch (error) { ipError.textContent = error.message; ipError.classList.remove("hidden"); }
});

loadBlockedIps().catch((error) => {ipError.textContent=error.message;ipError.classList.remove("hidden");});
loadBlockedDomains().catch((error) => {domainError.textContent=error.message;domainError.classList.remove("hidden");});

document.getElementById("domain-block-form").addEventListener("submit", async (event) => {
    event.preventDefault(); domainError.classList.add("hidden");
    try {
        await apiRequest("/api/ip/domain-blocklist", {method:"POST", body:JSON.stringify({domain:document.getElementById("blocked-domain").value,reason:document.getElementById("blocked-domain-reason").value})});
        event.target.reset(); await loadBlockedDomains();
    } catch (error) { domainError.textContent=error.message; domainError.classList.remove("hidden"); }
});
