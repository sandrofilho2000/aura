function toggleinstallmentCountField(){
  const id_billingType = document.getElementById("id_billingType")
  const id_installmentCount = document.getElementById("id_installmentCount")
  const field_installmentCount = document.querySelector(".field-installmentCount")

  const value = id_billingType.value
  if (!field_installmentCount) return
  
  if(value != 'CREDIT_CARD'){
    field_installmentCount.style.display = 'none'
    id_installmentCount.value = 1
  }else{
    field_installmentCount.style.display = 'block'
  }
}

async function fetchBillOnAsaas(){
  const asaasId = document.querySelector(".field-asaasId .readonly").innerText
}

document.addEventListener("DOMContentLoaded", async function () {
  id_billingType.addEventListener("change", toggleinstallmentCountField)
  toggleinstallmentCountField()
  await fetchBillOnAsaas()
})
    
