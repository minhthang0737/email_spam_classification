function showSettingsMessage(element, message, kind = "success") {
    element.textContent = message;
    element.className = `alert alert-${kind} mt-3 mb-0`;
}

document.getElementById("profile-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = document.getElementById("profile-message");
    message.classList.add("hidden");
    try {
        const data = await apiRequest("/api/account/profile", {method:"PUT", body:JSON.stringify({
            displayName:document.getElementById("profile-display-name").value,
            email:document.getElementById("profile-email").value,
        })});
        showSettingsMessage(message, data.message);
    } catch (error) {showSettingsMessage(message,error.message,"danger");}
});

document.getElementById("password-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = document.getElementById("password-message");
    const next = document.getElementById("new-password").value;
    if (next !== document.getElementById("confirm-password").value) {
        showSettingsMessage(message,"Hai mật khẩu mới không khớp.","danger"); return;
    }
    message.classList.add("hidden");
    try {
        const data = await apiRequest("/api/account/password", {method:"PUT", body:JSON.stringify({
            currentPassword:document.getElementById("current-password").value,
            newPassword:next,
        })});
        event.target.reset(); showSettingsMessage(message,data.message);
    } catch (error) {showSettingsMessage(message,error.message,"danger");}
});

const seedButton = document.getElementById("seed-all-demo-btn");
if (seedButton) seedButton.addEventListener("click", async () => {
    if (!confirm("Nhập bộ demo cho tất cả bảng? Email trùng sẽ được bỏ qua; mật khẩu analyst demo sẽ hiển thị sau khi hoàn tất.")) return;
    const message = document.getElementById("seed-all-message");
    seedButton.disabled=true; seedButton.textContent="Đang nhập bộ data lớn..."; message.classList.add("hidden");
    try {
        const data = await apiRequest("/api/demo/seed", {method:"POST"});
        const added = Object.entries(data.added).map(([table,count])=>`${table}: +${Number(count).toLocaleString("vi-VN")}`).join(" · ");
        const counts = Object.entries(data.counts).map(([table,count])=>`${table}: ${Number(count).toLocaleString("vi-VN")}`).join(" · ");
        showSettingsMessage(message,`${data.message} ${added}. Tổng hiện tại — ${counts}. Analyst demo: ${data.demoAnalyst.username} / ${data.demoAnalyst.password}`,"success");
    } catch (error) {showSettingsMessage(message,error.message,"danger");}
    finally {seedButton.disabled=false;seedButton.textContent="Nhập data cho mọi bảng";}
});
