document.addEventListener("DOMContentLoaded", function () {
    const handle_order_number = () =>{
        document.querySelectorAll("td.field-order").forEach((item, index) => {
            let new_img_input = item.querySelector("input")
            new_img_input.value = index + 1
            
        })
    }

    const handle_img_url = () =>{
        let new_img_tr = document.querySelectorAll("tr.form-row.dynamic-images")
        new_img_tr.forEach((item) => {
            let new_img_input = item.querySelector(".field-image_url input")
            let new_img = item.querySelector("img")
            
            new_img.addEventListener("error", (e)=>{
                e.target.src = "https://www.svgrepo.com/show/508699/landscape-placeholder.svg"
            })

            new_img_input.addEventListener("keyup", (e)=>{
                new_img.src = e.target.value.trim()
            })
        })
    }

    new Sortable(document.querySelector('.tabular.inline-related.last-related tbody'), {
        handle: 'td.drag', 
        onEnd: function(evt) {
          setTimeout(()=>{
              handle_order_number();
          }, 100)
        }
      });
  

    setTimeout(()=>{
        handle_order_number()
        handle_img_url()



        document.querySelectorAll("tr.add-row, td.delete").forEach((item)=>{
            item.addEventListener("click", ()=>{
                alert
                setTimeout(()=>{
                    handle_order_number()
                    handle_img_url()
                }, 100)
            })
        })
    }, 100)
})