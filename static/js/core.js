function toggleMenu() {
    const menu = document.getElementById('menu-lateral');
    if(menu) menu.classList.toggle('ativo');
}

function toggleNotificacoes() {
    const container = document.querySelector('.notificacao-container');
    if(container) container.classList.toggle('aberto');
}

window.onclick = function(event) {
    const modal = document.getElementById('modal-produto-overlay');
    if (event.target == modal) {
        modal.classList.add('hidden');
    }
}

function atualizarCatalogo() {
    // Só atualiza se estiver na aba do catálogo
    const catalogoAba = document.getElementById('Catalogo');
    if (catalogoAba && catalogoAba.classList.contains('active')) {
        fetch('/catalogo-atualizado/')
            .then(response => response.text())
            .then(html => {
                const gridProdutos = document.getElementById('grid-produtos');
                if (gridProdutos) {
                    gridProdutos.innerHTML = html;
                }
            })
            .catch(error => console.error('Erro ao atualizar catálogo:', error));
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Atualizar catálogo a cada 30 segundos
    setInterval(atualizarCatalogo, 30000);
    
    if (document.querySelector('[data-user-is-staff="true"]')) {
        carregarMensagensADM();
        // Atualizar mensagens do ADM a cada 10 segundos
        setInterval(carregarMensagensADM, 10000);
    }
});

// Função para carregar mensagens do ADM
    try {
        const response = await fetch('/chat/mensagens-adm/');
        if (response.ok) {
            const data = await response.json();
            atualizarListaChatADM(data.conversas);
        }
    } catch (error) {
        console.error('Erro ao carregar mensagens ADM:', error);
    }
}

function atualizarListaChatADM(conversas) {
    const lista = document.getElementById('lista-chat-adm');
    if (!lista) return;
    
    if (conversas.length === 0) {
        lista.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">Nenhuma mensagem nova.</p>';
        return;
    }
    
    let html = '';
    conversas.forEach(conversa => {
        html += `
            <div class="conversa-item" onclick="abrirConversaCliente(${conversa.cliente_id})" style="border: 1px solid #1b4f72; margin: 10px 0; padding: 15px; border-radius: 8px; cursor: pointer; transition: 0.2s ease;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: var(--verde);">${conversa.cliente_nome}</strong>
                        <p style="margin: 5px 0; color: #ccc; font-size: 0.9rem;">${conversa.ultima_msg}</p>
                    </div>
                    <div style="text-align: right;">
                        <small style="color: #888;">${conversa.data}</small>
                        <div style="background: var(--verde); color: black; border-radius: 50%; width: 20px; height: 20px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.8rem; margin-top: 5px;">${conversa.total_msgs}</div>
                    </div>
                </div>
            </div>
        `;
    });
    
    lista.innerHTML = html;
}

function fecharChatADM() {
    const chatModal = document.getElementById('chat-adm-modal');
    if (chatModal) {
        chatModal.style.display = 'none';
    }
}

async function carregarMensagensConversa(clienteId) {
    try {
        const response = await fetch(`/chat/conversa/${clienteId}/`);
        if (response.ok) {
            const data = await response.json();
            renderizarConversaCompleta(data);
        } else {
            console.error('Erro ao carregar conversa');
        }
    } catch (error) {
        console.error('Erro ao carregar conversa:', error);
    }
}

// Função para renderizar conversa completa
    const mensagensDiv = document.getElementById('chat-adm-mensagens');
    if (!mensagensDiv) return;
    
    if (data.mensagens.length === 0) {
        mensagensDiv.innerHTML = '<div class="chat-info">Nenhuma mensagem nesta conversa ainda.</div>';
        return;
    }
    
    let html = `<div class="chat-info">Conversa com <strong>${data.cliente_nome}</strong></div>`;
    
    data.mensagens.forEach(msg => {
        const classeMensagem = msg.is_adm ? 'mensagem-adm' : 'mensagem-cliente';
        let conteudoExtra = '';
        
        if (msg.arquivo_url) {
            // Verificar se é vídeo ou imagem baseado na extensão
                conteudoExtra = `<video src="${msg.arquivo_url}" controls width="200"></video>`;
            } else {
                conteudoExtra = `<img src="${msg.arquivo_url}" width="200" style="border-radius: 8px;">`;
            }
        }
        
        // Mostrar nome do remetente se for ADM (útil quando múltiplos ADMs)
        
        html += `
            <div class="${classeMensagem}">
                ${nomeRemetente}
                <p>${msg.texto}</p>
                ${conteudoExtra}
                <small style="font-size: 0.7rem; opacity: 0.7; display: block; margin-top: 5px;">
                    ${msg.data_envio}
                </small>
            </div>
        `;
    });
    
    mensagensDiv.innerHTML = html;
    // Scroll para o final
    mensagensDiv.scrollTop = mensagensDiv.scrollHeight;
}

// Função para ADM enviar mensagem para cliente
    const input = document.getElementById('chat-adm-input');
    const arquivoInput = document.getElementById('chat-adm-file');
    const chatModal = document.getElementById('chat-adm-modal');
    const clienteId = chatModal ? chatModal.dataset.clienteId : null;
    
    if (!clienteId) {
        alert('Cliente não identificado');
        return;
    }
    
    const texto = input.value.trim();
    const arquivo = arquivoInput.files[0];

    if (!texto && !arquivo) return;

    // Pegamos o token de segurança do Django (CSRF)
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
const formData = new FormData();
    formData.append('texto', texto);
    formData.append('destinatario_id', clienteId); // Enviar para o cliente específico
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
            renderizarMensagemADM(texto, arquivo);
            renderizarMensagemADM(texto, arquivo);
            alert('Erro ao enviar mensagem');
        }
    } catch (error) {
        console.error("Erro ao enviar mensagem ADM:", error);
        alert("Erro ao conectar com o servidor");
    }
}

// Função visual para mostrar mensagem enviada pelo ADM
function renderizarMensagemADM(texto, arquivo) {
    const lista = document.getElementById('chat-adm-mensagens');
    
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
        <div class="mensagem-adm">
            <p>${texto}</p>
            ${conteudoExtra}
        </div>
    `;
    
    // Scroll para o final
    lista.scrollTop = lista.scrollHeight;
}

// Ftion abrirConversaCliente(clienteId) {
    // Criar ou mostrar modal de chat ADM
    let chatModal = document.getElementById('chat-adm-modal');
        chatModal = document.createElement('div');
        chatModal.id = 'chat-adm-modal';
        chatModal.className = 'chat-modal';
        chatModal.innerHTML = `
            <div class="chat-overlay" onclick="fecharChatADM()"></div>
            <div class="chat-container">
                <div class="chat-header">
                    <h3>Chat com Cliente</h3>
                    <button onclick="fecharChatADM()" class="btn-fechar">×</button>
                </div>
                <div id="chat-adm-mensagens" class="chat-mensagens"></div>
                <div class="chat-input-area">
                    <input type="text" id="chat-adm-input" placeholder="Digite sua resposta..." onkeypress="if(event.key=='Enter') enviarMensagemADM()">
                    <input type="file" id="chat-adm-file" accept="image/*,video/*" style="display:none">
                    <button onclick="document.getElementById('chat-adm-file').click()" class="btn-anexo">📎</button>
                    <button onclick="enviarMensagemADM()" class="btn-enviar">Enviar</button>
                </div>
            </div>
        `;
        document.body.appendChild(chatModal);
    }
    
    // Armazenar cliente atual
    chatModal.dataset.clienteId = clienteId;
    chatModal.style.display = 'block';
    
    // Carregar histórico de mensagens desta conversa
    