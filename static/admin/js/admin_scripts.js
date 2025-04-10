document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/admin-token/", {
        method: "GET",
        credentials: "include"  // Envia os cookies do Django Admin para autenticação
    })
    .then(response => {
        if (!response.ok) throw new Error(`Erro: ${response.status}`);
        return response.json();
    })
    .then(data => {
        if (data.access) {
            document.cookie = `jwt=${data.access}; path=/`;  
        }
    })
    .catch(error => console.error("Erro ao obter token JWT:", error));
});
