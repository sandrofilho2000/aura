document.addEventListener("DOMContentLoaded", ()=>{
    if (document.querySelector("body.model-group .field-pages")) {
        let select_all_wrapper = document.createElement("div");
        select_all_wrapper.innerHTML = `
            <label for="id_pages_select_all">
                <input type="checkbox" name="select_all" value="3" id="id_pages_select_all"> Selecionar todos
            </label>
        `;
        console.log("select_all_wrapper: ", select_all_wrapper);

        document.querySelector("body.model-group .field-pages #id_pages").insertAdjacentElement("afterbegin", select_all_wrapper);

        select_all_wrapper.querySelector("input").addEventListener("change", (e)=>{
            e.target.closest("#id_pages").querySelectorAll('label input').forEach((item)=>{
                item.checked = e.target.checked
            })
        })
    } 
    if (document.querySelector("body.model-group .field-subpages")) {
        let select_all_wrapper = document.createElement("div");
        select_all_wrapper.innerHTML = `
            <label for="id_subpages_select_all">
                <input type="checkbox" name="select_all" value="3" id="id_subpages_select_all"> Selecionar todos
            </label>
        `;
        console.log("select_all_wrapper: ", select_all_wrapper);

        document.querySelector("body.model-group .field-subpages #id_subpages").insertAdjacentElement("afterbegin", select_all_wrapper);

        select_all_wrapper.querySelector("input").addEventListener("change", (e)=>{
            e.target.closest("#id_subpages").querySelectorAll('label input').forEach((item)=>{
                item.checked = e.target.checked
            })
        })
    } 
})