async function calcularFrete() {
    const cepDestino = document.getElementById('cep-input').value;
    const resultadoDiv = document.getElementById('resultado-frete');

    if (cepDestino.length !== 8) {
        alert("Por favor, digite um CEP válido com 8 números.");
        return;
    }

    resultadoDiv.innerHTML = "Calculating shipping...";

    try {
        const response = await fetch(`/calcular-frete/?cep=${cepDestino}`);
        const dados = await response.json();

        if (dados.error) {
            resultadoDiv.innerHTML = "Erro ao calcular frete.";
            return;
        }

        resultadoDiv.innerHTML = ""; 
        dados.forEach(opcao => {
            if (opcao.price) {
                resultadoDiv.innerHTML += `
                    <div class="opcao-frete" style="border: 1px solid #1b4f72; padding: 10px; margin-top: 5px; border-radius: 5px;">
                        <strong>${opcao.name}</strong>: R$ ${opcao.price} 
                        <small>(${opcao.delivery_range.min}-${opcao.delivery_range.max} dias)</small>
                        <button onclick="selecionarFrete('${opcao.price}', '${opcao.name}')">Selecionar</button>
                    </div>
                `;
            }
        });

    } catch (error) {
        console.error("Erro:", error);
        resultadoDiv.innerHTML = "Erro de conexão com o servidor.";
    }
}

function selecionarFrete(valor, nome) {
    alert(`Frete ${nome} de R$ ${valor} selecionado!`);
    // Aqui você pode salvar o valor no seu carrinho do