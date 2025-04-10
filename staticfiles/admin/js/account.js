function format_cpf_cnpj(){
    let value = document.getElementById('id_cpf_cnpj').value
    value = value.replace(/\D/g, ''); 

    if (value.length === 11) {
        value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    }

    else if (value.length === 14) {
        value = value.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    }

    document.getElementById('id_cpf_cnpj').value = value
}

function fill_cep(){
    const cepInput = document.getElementById('id_postal_code');
    const cepValue = cepInput.value.replace(/\D/g, ''); 

    if (cepValue.length === 8) { 
    // Realiza a requisição para a API dos Correios
    fetch(`https://viacep.com.br/ws/${cepValue}/json/`)
        .then(response => response.json())
        .then(data => {
        // Verifica se a API retornou os dados corretamente
        if (!data.erro) {
            // Preenche os campos com os dados retornados
            document.getElementById('id_address').value = data.logradouro || '';  // Endereço
            document.getElementById('id_complement').value = data.complemento || '';  // Complemento
            document.getElementById('id_province').value = data.bairro || '';  // Bairro
            document.getElementById('id_address_number').value = '';  // Número (pode ser deixado vazio, pois não vem no retorno)
        } else {
            alert('CEP não encontrado.');
        }
        })
        .catch(error => {
        console.error('Erro ao buscar o CEP:', error);
        alert('Erro ao buscar o CEP.');
        });
    } else {
    alert('CEP inválido.');
    }
}

function format_mobile_phone() {
    let value = document.getElementById('id_mobile_phone').value;
    value = value.replace(/\D/g, ''); 

    if (value.length === 11) {
        value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    } else if (value.length === 10) {
        value = value.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    }

    document.getElementById('id_mobile_phone').value = value;
}

document.addEventListener("DOMContentLoaded", function(){
    // Inicializando as funções
    format_cpf_cnpj();
    document.getElementById('id_cpf_cnpj').addEventListener("blur", format_cpf_cnpj);
    
    document.getElementById('id_postal_code').addEventListener("change", fill_cep);
    
    format_mobile_phone();
    document.getElementById('id_mobile_phone').addEventListener("blur", format_mobile_phone);
});
