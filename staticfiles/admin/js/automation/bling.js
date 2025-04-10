let codigoInput = document.querySelector("#codigo");
let codigo = `SOMDATERRA${Math.floor(100000 + Math.random() * 900000)}`;
codigoInput.value = codigo;

const image_list = [
    {
        "ordem": 1,
        "src": "https://http2.mlstatic.com/D_NQ_NP_2X_767706-MLU71707223158_092023-F.webp"
    },
    {
        "ordem": 1,
        "src": "https://http2.mlstatic.com/D_NQ_NP_2X_936010-MLU73982496250_012024-F.webp"
    },
    {
        "ordem": 1,
        "src": "https://http2.mlstatic.com/D_NQ_NP_2X_707204-MLU74143244293_012024-F.webp"
    },
    {
        "ordem": 2,
        "src": "https://http2.mlstatic.com/D_NQ_NP_2X_973521-MLU74021435748_012024-F.webp"
    },
    {
        "ordem": 3,
        "src": "https://http2.mlstatic.com/D_NQ_NP_2X_651383-MLU74089589550_012024-F.webp"
    }
]

// Ordena as imagens pela ordem antes de inseri-las
image_list.sort((a, b) => a.ordem - b.ordem);
console.log("🚀 ~ image_list ordenada:", image_list);

const newImgInput = document.querySelector("#urlImagemExt");
const addBtn = document.querySelector("a[data-id=aNovaLinhaImagemExterna]");

if (newImgInput && addBtn) {
    console.log("Ordem final das imagens antes da inserção:", image_list);

    image_list.forEach((image, index) => {
        setTimeout(() => {
            newImgInput.value = image.src;
            setTimeout(() => {
                addBtn.click();
                
                // Aguarda um tempo para que o novo input seja criado antes de adicionar a imagem
                setTimeout(() => {
                    criarImagem(); // Chama a função para criar a imagem após adicionar o novo campo de input
                }, 1000);
            }, 100);
        }, index * 300);
    });

    // Chama a função para criar imagens no início também, caso haja imagens para adicionar inicialmente
    setTimeout(() => {
        criarImagem();
    }, 1000);

} else {
    console.error("Elemento não encontrado: Verifique se #urlImagemExt e [data-id=aNovaLinhaImagemExterna] existem no DOM.");
}

// Função para criar um elemento de imagem com base no último campo de input gerado
function criarImagem() {
    document.querySelectorAll(".ui-sortable tr").forEach((tr) => {
        const lastInput = tr.querySelector("input"); // Pegando o input diretamente
        if (lastInput) {
            const src = lastInput.value; // Pega o valor do input
            if (src) {
                if(!tr.querySelector(".image")){
                    const img = document.createElement("img");
                    img.classList.add("image")
                    img.src = src;
                    img.style.width = "70px"; 
                    img.style.height = "70px"; 
                    img.style.border = "1px solid #000";
                    img.style.margin = "10px";
    
                    // Insere a imagem no 5º td
                    const td = tr.querySelector("td:nth-child(5)");
                    if (td) {
                        td.appendChild(img);
                        console.log("Imagem criada:", img);
                    }
                }
            }
        }
    });
}
