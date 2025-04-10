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

function generatePeriodLabels(period, count) {
    const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    const year = document.querySelector("select.monthly-select").value;  // Ano fixo
    const month = parseInt(document.querySelector("select.daily-select").value, 10) - 1;  // Mês fixo (começa de 0)
    const labels = [];
    const filters = [];

    // Ajusta a visibilidade das opções
    document.querySelectorAll(".period-helper-select").forEach((item) => {
        if (item.classList.contains(`${period}-select`)) {
            item.style.display = 'inline-block';
        } else {
            item.style.display = 'none';
        }
    });

    // Função para verificar se o ano é bissexto
    function isLeapYear(year) {
        return (year % 4 === 0 && year % 100 !== 0) || (year % 400 === 0);
    }

    // Função para pegar o número de dias do mês, levando em conta o ano bissexto
    function getDaysInMonth(month, year) {
        if ([0, 2, 4, 6, 7, 9, 11].includes(month)) {
            return 31;
        }
        if ([3, 5, 8, 10].includes(month)) {
            return 30;
        }
        return isLeapYear(year) ? 29 : 28;  // Fevereiro
    }

    if (period === 'monthly') {
        for (let i = 0; i < count; i++) {
            const monthIndex = (12 - count + i) % 12;
            const label = `${months[monthIndex]} ${year}`;
            labels.push(label);
            filters.push({ field: 's.date', value: `${year}-${(monthIndex + 1).toString().padStart(2, '0')}`, operation: 'LIKE' });
        }
        
    } else if (period === 'daily') {
        // Para o período diário, ajusta o número de dias de acordo com o mês e ano
        const daysInMonth = getDaysInMonth(month, year);
        for (let i = 1; i <= daysInMonth; i++) {
            const label = `${i}/${month + 1}`;
            labels.push(label);
            // Para o filtro diário, criamos o "MAIOR_IGUAL" e "MENOR_IGUAL"
            if (i === 1) {
                const startDate = `${year}-${(month + 1).toString().padStart(2, '0')}-01`;  // Primeiro dia do mês
                filters.push({ field: 's.date', value: startDate, operation: 'MAIOR_IGUAL' });
            }
            if (i === daysInMonth) {
                const endDate = `${year}-${(month + 1).toString().padStart(2, '0')}-${daysInMonth.toString().padStart(2, '0')}`;  // Último dia do mês
                filters.push({ field: 's.date', value: endDate, operation: 'MENOR_IGUAL' });
            }
        }
    } else if (period === 'yearly') {
        for (let i = 0; i < count; i++) {
            const label = `${year - i}`;
            labels.push(label);
            filters.push({ field: 's.date', value: `${year - i}`, operation: 'LIKE' });
        }
    }

    return { labels: labels, filters: filters };
}

// Função de vendas, ajustada para aceitar o período
function sales_volume(labels, sales) {
    const sales_volume_ctx = document.getElementById('sales_volume').getContext('2d');

    if (sales_volume_ctx) {
        // Agrupar as vendas por data
        const salesByDate = sales.reduce((acc, sale) => {
            let saleDate = sale.date; 
            saleDate= new Date(saleDate);

            const month = saleDate.getMonth() + 1;  // Adiciona 1 para ajustar ao formato usual de meses
            const day = saleDate.getDate();  // Obtém o dia do mês
            
            saleDate = `${day}/${month}`;
            console.log("🚀 ~ salesByDate ~ saleDate:", saleDate)
            if (acc[saleDate]) {
                acc[saleDate] += 1;  // Incrementa a contagem de vendas para essa data
            } else {
                acc[saleDate] = 1;  // Inicia a contagem de vendas para essa data
            }
            return acc;
        }, {});

        // Contar as vendas para cada data nos labels
        const salesData = labels.map(label => {
            return salesByDate[label] || 0;  // Se não houver vendas para essa data, retorna 0
        });

        // Configuração dos dados para o gráfico
        const sales_volume_data = {
            labels: labels,  // Labels são as datas
            datasets: [{
                label: 'Vendas',
                data: salesData,  // As contagens de vendas por data
                fill: false,
                borderColor: '#ef476f',
                tension: 0.1
            }]
        };

        // Configuração do gráfico
        const sales_volume_config = {
            type: 'line',
            data: sales_volume_data,
            options: {
                responsive: true, 
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Volume de vendas',
                        font: { size: 18 }
                    },
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                }
            }
        };

        // Atualiza ou cria o gráfico
        if (window.salesIncomeChart) {
            window.salesIncomeChart.destroy();  // Remove o gráfico anterior
        }

        window.salesIncomeChart = new Chart(sales_volume_ctx, sales_volume_config);  // Cria o gráfico com novos dados
    }
}

// Função de canais de vendas (inalterada)
function sales_channels(sales = []) {
    const sales_channel_ctx = document.getElementById('sales_channel').getContext('2d');

    if (sales_channel_ctx && sales.length) {
        const channelCount = {};

        sales.forEach(sale => {
            channelCount[sale.sale_channel_name] = (channelCount[sale.sale_channel_name] || 0) + 1;
        });
        
        const channelNames = Object.keys(channelCount);
        const channelCounts = Object.values(channelCount);
        const colors = [
            '#9e61c7', '#e63946', '#457b9d', '#f4a261', '#2a9d8f', 
            '#e76f51', '#3a86ff', '#ffbe0b', '#ffbe0b', '#ef476f',
            '#118ab2', '#f3722c', '#8338ec', '#8ac926', '#fb5607'
        ];

        const sales_channel_data = {
            labels: channelNames,
            datasets: [{
                label: 'Canais de venda',
                data: channelCounts,
                backgroundColor: colors,
                hoverOffset: 4
            }]
        };

        const sales_channel_config = {
            type: 'pie',
            data: sales_channel_data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Canais de venda',
                        font: { size: 18 }
                    },
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                }
            }
        };

        // Destruir o gráfico anterior, se existir
        if (window.salesChannelChart) {
            window.salesChannelChart.destroy();  // Remove o gráfico anterior
        }

        // Criar o novo gráfico
        window.salesChannelChart = new Chart(sales_channel_ctx, sales_channel_config);
    }
}

// Função para buscar os dados de vendas da API
async function fetchSalesData(filters=[{ field: 's.date', value: '2025', operation: 'LIKE' }]) {
    const params = {
        app: 'sales_sale',
        fields: ["s.id AS sale_id", "s.title", "s.discount AS sale_discount", "s.date", "s.total_price AS sale_total_price", 
                "sc.name AS sale_channel_name", "au.first_name AS seller_first_name", "cc.first_name AS client_first_name",
                "STRING_AGG(pp.name, '--- ') AS product_names", "SUM(sp.discount) AS total_product_discount", 
                "SUM(sp.qtn) AS total_quantity"],
        filters: filters
    };

    const apiUrl = `/api/sales_api?app=${encodeURIComponent(params.app)}&fields=${encodeURIComponent(params.fields.join(','))}&filters=${encodeURIComponent(JSON.stringify(params.filters))}`;

    try {
        const response = await fetch(apiUrl);

        if (!response.ok) {
            throw new Error(`Erro na requisição: ${response.statusText}`);
        }

        
        const data = await response.json();
        const items = data.items || []
        const info_sales = items.length || 0


        const info_items = items.reduce((total, item) => {
            console.log("🚀 ~ constinfo_items=items.reduce ~ item:", item)
            return total + item.products.reduce((sum, product) => sum + product.product_qtn, 0);
        }, 0);

        const info_income = 123444
        const info_avg = info_income / info_sales

        document.querySelector("#info-sales span.info-sales-value").innerHTML = info_sales
        document.querySelector("#info-items span.info-items-value").innerHTML = info_items
        document.querySelector("#info-income span.info-income-value").innerHTML = passToCurrency(info_income)
        document.querySelector("#info-avg span.info-avg-value").innerHTML = passToCurrency(info_avg)
        return items;

    } catch (error) {
        console.error('Erro ao buscar dados de vendas:', error);
        return { message: 'Erro ao buscar dados', error: error.message };
    }
}

// Inicializa o gráfico com o período escolhido e dados das vendas
document.addEventListener("DOMContentLoaded", async function () {
    const period = document.querySelector("#period-select").value || 'daily'
    let {labels, filters} =  generatePeriodLabels(period, 12); 

    let sales = await fetchSalesData(filters);

    sales_channels(sales);
    sales_volume(labels, sales);  
    
    document.querySelectorAll('.select_fields select').forEach((select)=>{
        select.addEventListener('change', async (e) => {
            const period = document.querySelector("#period-select").value || 'daily'
            let {labels, filters} =  generatePeriodLabels(period, 12); 
            let sales = await fetchSalesData()
            sales_channels(sales);
            sales_volume(labels, sales);  
        });
    });
});
