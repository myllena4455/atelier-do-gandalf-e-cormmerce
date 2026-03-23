// Funções Visuais Essenciais
function toggleMenu() {
    const menu = document.getElementById('menu-lateral');
    if(menu) menu.classList.toggle('ativo');
}

function toggleNotificacoes() {
    const container = document.querySelector('.notificacao-container');
    if(container) container.classList.toggle('aberto');
}

// Fechar modais ao clicar fora
window.onclick = function(event) {
    const modal = document.getElementById('modal-produto-overlay');
    if (event.target == modal) {
        modal.classList.add('hidden');
    }
}

// Atualização automática do catálogo a cada 30 segundos
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

// Iniciar atualização automática quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    // Atualizar catálogo a cada 30 segundos
    setInterval(atualizarCatalogo, 30000);
});