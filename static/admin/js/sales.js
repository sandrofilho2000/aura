function ParseFloat(str) {
    str = str.toString();
    if(str.split(".").length != 1){
        str = str.slice(0, (str.indexOf(".")) + 2 + 1); 
    }
    return Number(str);   
}

function passToCurrency(num=0) {
    num = Number(num).toFixed(2)
    
    if (isNaN(num)) {
        return 0
    }

    var str_split = String(num).split('.');
    let valor = num ? String(num) : '0';
    valor = valor.replaceAll('.', '');
    valor = valor.replaceAll(',', '.');
    valor = valor.replaceAll('R$', '');
    valor = Number(valor.trim());
  
/*     if (str_split.slice(-1)[0].length == 3) {
      valor = valor / 1000;
    } */
  
    if (str_split.slice(-1)[0].length == 2) {
      valor = valor / 100;
    }
    
    if (str_split.slice(-1)[0].length == 1) {
      valor = valor / 10;
    }
  
    let newValor = valor.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    });

    return newValor;
};

function passToNumber(str="0"){
    str = String(str)
    str = str.replace(/[^\d.,]/g, '')

    let number = 0;
    let str_has_commas = str.split(",").length > 1
    let str_has_dots = str.split(".").length > 1
    
    //50,00 OUTPUT: 50.00
    if( str_has_commas && !str_has_dots){
        number = Number(str.replaceAll(",", "."))
    }
    
    //50.00 OUTPUT: 50.00
    else if( !str_has_commas && str_has_dots){
        number = ParseFloat(str)
    }

    //R$ 2,790.00 OUTPUT: 2790.00
    else if( str_has_commas && str_has_dots){
        number = str.replaceAll(".", "*")
        number = number.replaceAll(",", ".")
        number = number.replaceAll("*", "")
    }
    
    number = Number(number)
    number = ParseFloat(number)
    return number
}

function setSaleTotalPrice(){
    let discount = 0
    if(document.querySelector("#sale_form input#id_discount")){
        discount = document.querySelector("#sale_form input#id_discount").value
    }else{
        discount = passToNumber(document.querySelector("#sale_form .field-discount .readonly").innerText)
    }

    let subtotal = 0

    if (discount < 0){
        discount = 0
    }
    
    document.querySelectorAll(".dynamic-products .field-total_price p").forEach((item)=>{
        let product_total = item.innerText
        product_total = passToNumber(product_total)
        subtotal+=product_total
    })

    
    let total = subtotal
    discount = subtotal * (discount / 100)
    total -= discount

    document.querySelector("#sale_form .field-total_price .readonly").innerText = passToCurrency(total)
    document.querySelector("#sale_form .field-subtotal_price .readonly").innerText = passToCurrency(subtotal)

    if(document.querySelectorAll(".dynamic-products .field-supplier_price p").length){
        let supplier_price = 0
        document.querySelectorAll(".dynamic-products .field-supplier_price p").forEach((item)=>{
            let supplier_product_price = item.innerHTML
            if (supplier_product_price){
                supplier_product_price = passToNumber(supplier_product_price)
                supplier_price+=supplier_product_price
            }
        })
    
        let profit = total - supplier_price
        let profit_percentage = (profit / supplier_price) * 100 || 0;
        let supplier_price_percentage = 100 - profit_percentage || 0 
        
    
        document.querySelector("#sale_form .field-supplier_price .readonly").innerHTML = `${passToCurrency(supplier_price)} <small>(${supplier_price_percentage.toFixed(2)}%)</small>`
        document.querySelector("#sale_form .field-profit .readonly").innerHTML = `${passToCurrency(profit)} <small>(${profit_percentage.toFixed(2)}%)</small>`
    }


}

async function observeSelect2Changes(element_id="") {
    const select2RenderedElement = document.querySelector(`tbody #${element_id} .select2-selection__rendered`);
    if (select2RenderedElement) {
        const observer = new MutationObserver(async (mutations, observer) => {
            let mutation = mutations[0]
                if (mutation.type === 'childList' || mutation.type === 'subtree') {
                    if(mutation.target.innerText){
                        let code = mutation.target.innerText.split(" | ")[0]
                        code = code.split(")")[0]
                        code = code.replaceAll("(", "")
                        
                        document.querySelector(`tbody #${element_id}`).classList.add("loading")

                        let data = await fetch_admin_api("product", "code" , code)
                        document.querySelector(`tbody #${element_id}`).classList.remove("loading")
                        
                        if (data.status !== 200){
                            alert(data.message)
                            return 
                        }

                        let {items} = data
                        console.log("🚀 ~ observer ~ items:", items)

                        if (items.length){
                            let price = items[0].final_price
                            let supplier_price = items[0].supplier_price
                            document.querySelector(`tbody #${element_id} .field-total_price p`).innerHTML = passToCurrency(price)
                            document.querySelector(`tbody #${element_id} .field-single_price p`).innerHTML = passToCurrency(price)

                            if(document.querySelector(`tbody #${element_id} .field-supplier_price p`)){
                                document.querySelector(`tbody #${element_id} .field-supplier_price p`).innerHTML = passToCurrency(supplier_price)
                                document.querySelector(`tbody #${element_id} .field-supplier_price p`).setAttribute("single_supplier_price", supplier_price) 
                            }

                            updateProductTotal(element_id)
                        }

                        let howManyNewProductFormsAreOpened = 0
                        document.querySelectorAll("tbody tr .field-supplier_price").forEach((item)=>{
                            if (item.innerText == "-"){
                                howManyNewProductFormsAreOpened++
                            }
                        })

                        if (!howManyNewProductFormsAreOpened){
                            document.querySelector("tr.add-row td a").click()
                        }
                    }
                }
            
        });

        const config = { childList: true, subtree: true };

        observer.observe(select2RenderedElement, config);

    }
}

async function areProductsLoading(element_id = "") {
    const row = document.querySelector(`tbody #${element_id}`);
    if (row) {
        return new Promise((resolve) => {
            const myInterval = setInterval(() => {
                const isLoading = document.querySelectorAll('.select2-results__option.loading-results').length !== 0;
                if (!isLoading) {
                    clearInterval(myInterval);
                    resolve(false); 
                }
            }, 100);
        });
    }
    return Promise.resolve(false); 
}

function updateProductIndex(){
    document.querySelectorAll(".js-inline-admin-formset table tr.form-row").forEach((item, index)=>{
        if(item.querySelector("td.item_index")){
            item.querySelector("td.item_index").innerText = `#${index + 1}`
        }
    })
}

function setProductSinglePrice(first_load=false) {

    document.querySelectorAll(".tabular.inline-related.last-related tr.form-row").forEach((item)=>{
        let element_id = item.closest("tr").id
        item.querySelector(".field-qtn input").addEventListener('change', ()=>{updateProductTotal(element_id)})
        if(item.querySelector(".field-discount input")){
            
            setTimeout(()=>{
                updateProductTotal(element_id)
            }, 100)

            item.querySelector(".field-discount input")?.addEventListener('change', ()=>{updateProductTotal(element_id)})
            
        }
    })

    let query = first_load ? ".tabular.inline-related.last-related tr.form-row .select2-selection.select2-selection--single" : ".tabular.inline-related.last-related tr.form-row:not(.has_original) .select2-selection.select2-selection--single:not(.has_event_listener)" 
    
    document.querySelectorAll(query).forEach(async (item) => {

        let element_id = item.closest("tr").id

        if (item.innerText){
            let code = item.innerText.split(" | ")[0]
            code = code.split(")")[0]
            code = code.replaceAll("(", "")

            document.querySelector(`tbody #${element_id}`).classList.add("loading")
            let data = await fetch_admin_api("product", "code" , code)
            document.querySelector(`tbody #${element_id}`).classList.remove("loading")
            
            if (data.status !== 200){
                alert(data.message)
                return 
            }

            let {items} = data

            if (items.length){
                let price = items[0].final_price
                let supplier_price = items[0].supplier_price
                let qtn = document.querySelector(`tbody #${element_id} .field-qtn input`).value
                
                let total = Number(price) * Number(qtn)

                document.querySelector(`tbody #${element_id} .field-total_price p`).innerHTML = passToCurrency(total)
                document.querySelector(`tbody #${element_id} .field-single_price p`).innerHTML = passToCurrency(price)

                if(document.querySelector(`tbody #${element_id} .field-supplier_price p`)){
                    document.querySelector(`tbody #${element_id} .field-supplier_price p`).innerHTML = passToCurrency(supplier_price)
                    document.querySelector(`tbody #${element_id} .field-supplier_price p`).setAttribute("single_supplier_price", supplier_price) 
                }

                updateProductTotal(element_id)
            }
        }
        
        item.addEventListener("click", async function (e) {
            item.setAttribute("has_event_listener", true)
            item.closest("tr").classList.add("has_original")
            const isModelOpened = e.currentTarget.ariaExpanded === 'true';
            if (isModelOpened) {
                const productsAreLoading = await areProductsLoading(element_id);
                if(!productsAreLoading){
                    observeSelect2Changes(element_id)
                }
            }
        });
        
    })

}

function updateProductTotal(element_id=""){

    let price = passToNumber(document.querySelector(`tbody #${element_id} .field-single_price p`).innerText)
    let discount;

    if(document.querySelector(`tbody #${element_id} .field-discount input`)){
        discount = document.querySelector(`tbody #${element_id} .field-discount input`).value
    }else{
        discount = document.querySelector(`tbody #${element_id} .field-discount p`).innerText
    }

    let qtn = document.querySelector(`tbody #${element_id} .field-qtn input`).value || 1


    if (discount < 0){
        discount = 0
    }

    if(typeof price === "number"){
        let total = (price * qtn)
        
        if(discount > 0){
            discount = total * (discount / 100)
            total -= discount
        }   

        document.querySelector(`tbody #${element_id} .field-total_price p`).innerHTML = passToCurrency(total)

        if(document.querySelector(`tbody #${element_id} .field-supplier_price p`)){
            let supplier_price = document.querySelector(`tbody #${element_id} .field-supplier_price p`).getAttribute("single_supplier_price")
            document.querySelector(`tbody #${element_id} .field-total_price p`).innerHTML = passToCurrency(total)
      
            supplier_price = supplier_price * qtn
            if(supplier_price){
                let profit = total - supplier_price
                document.querySelector(`tbody #${element_id} .field-profit p`).innerHTML = passToCurrency(profit)
                document.querySelector(`tbody #${element_id} .field-supplier_price p`).innerHTML = passToCurrency(supplier_price)
            }
        }
        
        setSaleTotalPrice()
    }
}

function addEventListenerToRemoveItemsBtn(){
    document.querySelectorAll("table tr td.delete a.inline-deletelink").forEach((item)=>{
        item.addEventListener("click", setSaleTotalPrice)
    })
}

document.addEventListener("DOMContentLoaded", function(){
    setTimeout(()=>{
        if(document.querySelectorAll(".field-discount").length){
            setProductSinglePrice(first_load=true)
            document.querySelector("#sale_form input#id_discount")?.addEventListener("change", setSaleTotalPrice)
            document.querySelector("tr.add-row").addEventListener("click", function(e){
                updateProductIndex()
                setTimeout(()=>{
                    setProductSinglePrice()
                    addEventListenerToRemoveItemsBtn()
                }, 100)
            })
        } 
    }, 200)
})


