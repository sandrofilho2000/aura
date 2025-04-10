async function fetch_admin_api(app = "", field = "", value = "", operation = "contains") {
    const apiUrl = `/api/search?app=${encodeURIComponent(app)}&field=${encodeURIComponent(field)}&value=${encodeURIComponent(value)}&operation=${encodeURIComponent(operation)}`;
    const response = await fetch(apiUrl);        
    const data = await response.json();
    return data
}