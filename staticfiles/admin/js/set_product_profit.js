function ParseFloat(str) {
    str = str.toString();
    if(str.split(".").length != 1){
        str = str.slice(0, (str.indexOf(".")) + 2 + 1); 
    }
    return Number(str);   
}

function setFinalPrice(e){
    let margin = Number(document.querySelector("#id_profit_margin").value) || 40
    if(margin <= 0){
        document.querySelector("#id_profit_margin").value = 1
        margin = 1
    }
    let supplier_price = Number(document.querySelector("#id_supplier_price").value) || 0
    
    if (supplier_price){
        let profit = supplier_price * (margin / 100)
        profit = profit + supplier_price
        if (profit){
            document.querySelector("#id_final_price").value = ParseFloat(profit)
        }                
    }
}

function setProfitMargin(e) {
    let final_price = Number(document.querySelector("#id_final_price").value);
    let supplier_price = Number(document.querySelector("#id_supplier_price").value) || 0;
    let margin = 0;

    // Check if supplier_price is not zero to avoid division by zero
    if (supplier_price > 0) {
        margin = ((final_price - supplier_price) / supplier_price) * 100;
    }

    document.querySelector("#id_profit_margin").value = parseFloat(margin.toFixed(2));
    return margin;
}

document.addEventListener("DOMContentLoaded", function () {
    if(document.querySelector("#id_profit_margin")){
        setFinalPrice()
        document.querySelector("#id_profit_margin").addEventListener("change", setFinalPrice)
        document.querySelector("#id_supplier_price").addEventListener("change", setFinalPrice)
    }
    if(document.querySelector("#id_final_price")){
        setProfitMargin()
        document.querySelector("#id_final_price").addEventListener("change", setProfitMargin)
        document.querySelector("#id_supplier_price").addEventListener("change", setProfitMargin)
    }
})