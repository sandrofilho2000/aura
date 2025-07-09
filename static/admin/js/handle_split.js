async function fetch_admin_api(app = "", field = "", value = "", operation = "equals") {
  const apiUrl = `/api/search?app=${encodeURIComponent(app)}&field=${encodeURIComponent(field)}&value=${encodeURIComponent(value)}&operation=${encodeURIComponent(operation)}`;
  const response = await fetch(apiUrl);
  const data = await response.json();
  return data
}

function handle_messagelist(type="error", messages){
  let main = document.querySelector("main#content-start")
  let messageList = document.querySelector("main ul.messagelist")
  if(!messageList){
    messageList = document.createElement("ul")
    messageList.classList.add("messagelist")
    messageList.innerHTML = "TESTE"
    main.prepend(messageList);
  }

  messages.forEach(message=>{
    li = document.createElement("li")
    li.classList.add(type)
    li.innerText = message
    messageList.prepend(li)
  })
}

function getCSRFToken() {
  const cookieValue = document.cookie
    .split("; ")
    .find(row => row.startsWith("csrftoken="));
  return cookieValue ? cookieValue.split("=")[1] : null;
}


function getJWT() {
  const cookies = document.cookie.split("; ").reduce((acc, cookie) => {
    const [key, value] = cookie.split("=");
    acc[key] = value;
    return acc;
  }, {});
  return cookies["jwt"];
}

async function create_billing(billing) {
  try {
    const csrfToken = getCSRFToken();

    const response = await fetch('/api/create-billing', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        "Authorization": `Bearer ${getJWT()}`,
        'X-CSRFToken': csrfToken,
      },
      credentials: 'include',
      body: JSON.stringify(billing)
    });

    if (!response.ok) {
      throw new Error(`Erro: ${response.status}`);
    }

    const data = await response.json();
    return data;

  } catch (error) {
    console.error("Erro ao criar link de pagamento:", error);
    return null; // para garantir que `response` não seja undefined
  }
}








async function handle_default_commissions(item) {
  debugger
  const tr_num = item.id.split("-")[1];
  const subaccount_id = item.querySelector(".field-subaccount select").value;
  if (!subaccount_id) return;

  item.classList.add("loading");

  const { results } = await fetch_admin_api("subaccount", "id", subaccount_id);
  const { fixedValue, percentualValue } = results[0];

  if (percentualValue) {
    item.querySelector(".field-percentualValue input").value = percentualValue;
  }


  if (fixedValue) {
    item.querySelector(".field-fixedValue input").value = fixedValue;
  }
  
  

  item.classList.remove("loading");
}

const eventListenersMap = new WeakMap();

function add_event_listeners_to_fields() {
  document.querySelectorAll("tr.form-row:not(.has_original)").forEach((item) => {

    if (eventListenersMap.has(item)) {
      const { changeListeners } = eventListenersMap.get(item);

      item.querySelectorAll("input:not([type='hidden']), .field-subaccount select").forEach((input_select, index) => {
        input_select.removeEventListener("change", changeListeners[index]);
      });
    }

    const changeListeners = [];

    item.querySelectorAll("input:not([type='hidden']), .field-subaccount select").forEach((input_select) => {
      const changeListener = () => handle_default_commissions(item);
      changeListeners.push(changeListener);
      input_select.addEventListener("change", changeListener);
    });

    eventListenersMap.set(item, { changeListeners });
  });
}

document.addEventListener("DOMContentLoaded", async function () {
  setTimeout(() => {
    document.querySelector("tr.add-row").addEventListener("click", function () {
      add_event_listeners_to_fields()
    })

    document.querySelectorAll("tr.form-row:not(.has_original)").forEach((item) => {
      add_event_listeners_to_fields()
    })
  }, 100)

  const billing_id = location.pathname.replace(/\D/g, "")
  
  if (!billing_id) return

  try {
    const [billingRes, subaccountsRes] = await Promise.all([
      fetch_admin_api("billing", "id", billing_id),
      fetch_admin_api("billingsplit", "billing_id", billing_id),
    ])

    let billing = billingRes.results[0]
    billing['split'] = subaccountsRes.results

    if (!billing.paylink) {
      const response = await create_billing(billing)
      console.log("🚀 ~ response:", response)
      if(response.status === 200){
        const {paylink, asaasId} = response
        document.querySelector(".field-paylink .readonly").innerHTML = `
        <a target="_blank" style="text-decoration: underline" href='${paylink}'>
          ${paylink}
        </a>
        `
        document.querySelector(".field-asaasId .readonly").innerText = asaasId
      }else{
        const messages = response.errors.map(
          (error) => `Erro ao criar cobrança Asaas: ${error.description}`
        );
        
        handle_messagelist("error", messages);
      }
    }else{
      const paylink = document.querySelector(".field-paylink .readonly").innerHTML

      document.querySelector(".field-paylink .readonly").innerHTML = `
      <a target="_blank" style="text-decoration: underline" href='${paylink}'>
        ${paylink}
      </a>
      `
    }

  } catch (err) {
    console.error("Erro ao buscar dados ou criar cobrança:", err)
  }

})
    

