function abrirChat(produtoId) {
    let chatModal = document.getElementById('chat-modal');
    if (!chatModal) {
        chatModal = document.createElement('div');
        chatModal.id = 'chat-modal';
        chatModal.className = 'chat-modal';
        chatModal.innerHTML = `
            <div class="chat-overlay" onclick="fecharChat()"></div>
            <div class="chat-container">
                <div class="chat-header">
                    <h3>Negociar Produto</h3>
                    <button onclick="fecharChat()" class="btn-fechar">×</button>
                </div>
                <div id="chat-mensagens" class="chat-mensagens"></div>
                <div class="chat-input-area">
                    <input type="text" id="chat-input" placeholder="Digite sua mensagem..." onkeypress="if(event.key=='Enter') enviarMensagem()">
                    <input type="file" id="chat-file" accept="image/*,video/*" style="display:none">
                    <button onclick="document.getElementById('chat-file').click()" class="btn-anexo">📎</button>
                    <button onclick="enviarMensagem()" class="btn-enviar">Enviar</button>
                </div>
            </div>
        `;
        document.body.appendChild(chatModal);
    }
    
    // Armazenar produto atual
    chatModal.style.display = 'block';
    
    // Carregar histórico de mensagens (se existir)
    carregarMensagens(produtoId);
}
// Enviar Mensagem (Texto ou Ficheiro)
async function enviarMensagem() {
    const arquivoInput = document.getElementById('chat-file');
    const texto = input.value.trim();
    const arquivo = arquivoInput.files[0];
    const chatModal = document.getElementById('chat-modal');
    const produtoId = chatModal ? chatModal.dataset.produtoId : null;

    if (!texto && !arquivo) return;

    // Pegamos o token de segurança do Django (CSRF)
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    formData.append('texto', texto);
    formData.append('destinatario_id', '1'); // ADM ID (ajuste conforme necessário)
    if (arquivo) {
        formData.append('arquivo', arquivo);
    }

    try {
        const response = await fetch('/enviar-mensagem/', {
            method: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            input.value = '';
            arquivoInput.value = '';
            // Atualiza o chat na tela
            renderizarMinhaMensagem(texto, arquivo);
        } else {
            
    } catch (error) {
        console.error("Erro ao enviar mensagem:", error);
    }
}

// Função visual para mostrar a mensagem na hora
function renderizarMinhaMensagem(texto, arquivo) {
    const lista = document.getElementById('chat-mensagens');
    let conteudoExtra = "";
    if (arquivo) {
        const urlSimulada = URL.createObjectURL(arquivo);
        if (arquivo.type.includes('video')) {
            conteudoExtra = `<video src="${urlSimulada}" controls width="200"></video>`;
        } else {
            conteudoExtra = `<img src="${urlSimulada}" width="200">`;
        }
    }

    lista.innerHTML += `
        <div class="mensagem-minha">
            <p>${texto}</p>
            ${conteudoExtra}
        </div>


    
    `;
}

async function enviarMensagemAdm(vendaId, novoPreco) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    const formData = new FormData();
    formData.append('venda_id', vendaId);
    formData.append('novo_preco', novoPreco);

    try {
        const response = await fetch('/chat/atualizar-orcamento/', {
            method: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            body: formData
        });
        
        if(response.ok) {
            alert("Orçamento atualizado e enviado ao cliente!");
        } else {
            alert("Erro ao atualizar orçamento");
        }
    } catch (error) {
        console.error("Erro:", error);
        alert("Erro ao conectar com o servidor");
    }
}

// Função para fechar o chat
function fecharChat() {
    const chatModal = document.getElementById('chat-modal');
    if (chatModal) {
    }
}

// Função para carregar mensagens do chat
async function carregarMensagens(produtoId) {
    // Por enquanto, apenas limpa as mensagens
    // Futuramente pode carregar histórico do banco
    const lista = document.getElementById('chat-mensagens');
        lista.innerHTML = '<p class="chat-info">Inicie a conversa para personalizar seu produto!</p>';
    }
}