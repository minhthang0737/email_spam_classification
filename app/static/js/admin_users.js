const usersBody = document.getElementById("users-body");
const usersError = document.getElementById("users-error");

function showUsersError(message) { usersError.textContent = message; usersError.classList.remove("hidden"); }
async function loadUsers() {
    const response = await apiRequest("/api/users");
    usersBody.replaceChildren();
    response.data.forEach((user) => {
        const row = document.createElement("tr");
        [user.username, user.role, user.isActive ? "Đang hoạt động" : "Đã khóa"].forEach((text) => { const cell=document.createElement("td");cell.textContent=text;row.appendChild(cell); });
        const actions = document.createElement("td");
        const toggle = document.createElement("button"); toggle.className="btn btn-sm btn-outline-secondary mr-1"; toggle.textContent=user.isActive?"Khóa":"Mở khóa";
        toggle.addEventListener("click", async()=>{try{await apiRequest(`/api/users/${user.id}`,{method:"PUT",body:JSON.stringify({isActive:!user.isActive,role:user.role})});await loadUsers();}catch(e){showUsersError(e.message);}});
        const role = document.createElement("button"); role.className="btn btn-sm btn-outline-primary mr-1"; role.textContent="Đổi vai trò";
        role.addEventListener("click", async()=>{const next=user.role==="admin"?"analyst":"admin";try{await apiRequest(`/api/users/${user.id}`,{method:"PUT",body:JSON.stringify({isActive:user.isActive,role:next})});await loadUsers();}catch(e){showUsersError(e.message);}});
        const del = document.createElement("button"); del.className="btn btn-sm btn-outline-danger";del.textContent="Xóa";
        del.addEventListener("click",async()=>{if(!confirm(`Xóa tài khoản ${user.username}?`))return;try{await apiRequest(`/api/users/${user.id}`,{method:"DELETE"});await loadUsers();}catch(e){showUsersError(e.message);}});
        actions.append(toggle,role,del);row.appendChild(actions);usersBody.appendChild(row);
    });
}
document.getElementById("user-form").addEventListener("submit",async(event)=>{
    event.preventDefault();usersError.classList.add("hidden");
    try{await apiRequest("/api/users",{method:"POST",body:JSON.stringify({username:document.getElementById("new-username").value,password:document.getElementById("new-password").value,role:document.getElementById("new-role").value})});event.target.reset();await loadUsers();}
    catch(e){showUsersError(e.message);}
});
loadUsers().catch((error)=>showUsersError(error.message));
