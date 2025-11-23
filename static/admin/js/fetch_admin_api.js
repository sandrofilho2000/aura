async function fetch_admin_api(app = "", field = "", value = "", operation = "contains") {
    const apiUrl = `/api/search?app=${encodeURIComponent(app)}&field=${encodeURIComponent(field)}&value=${encodeURIComponent(value)}&operation=${encodeURIComponent(operation)}`;
    const response = await fetch(apiUrl);        
    const data = await response.json();
    return data
}

document.addEventListener("DOMContentLoaded", function(){
    if(document.querySelector(".app-home")){
        if(this.location.pathname != "/admin/"){
            this.location.replace("/admin/")
        }
    }
})