///MERCADO LIVRE
let image_list = [];
let ordem = 1;
let num_of_images = document.querySelector(".pswp__counter").innerText;
num_of_images = num_of_images.split("/")[1] 
let intervalId;

const coletarImagem = () => {
    document.querySelectorAll("div.pswp__scroll-wrap img.pswp__img").forEach((img, index) => {
        if (!image_list.some(item => item.src === img.src)) {
            if (img.closest(".pswp__img").style.display !== "none") {
                image_list.push({ ordem, src: img.src });
                console.log("🚀 ~ Coletado:", ordem, img.src);
            }
        }
    });

    if (ordem >= (num_of_images*2)) {
        clearInterval(intervalId);
        console.log("Coleta finalizada!", image_list);
    }
};

// Coletar a primeira imagem antes de iniciar o loop
coletarImagem();

// Inicia o intervalo para capturar imagens
intervalId = setInterval(() => {
    document.querySelector(".pswp__button.pswp__button--arrow--right").click();
    ordem++;

    setTimeout(coletarImagem, 100);
}, 200);