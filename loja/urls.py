from django.urls import path
from . import views

urlpatterns = [
    # Página inicial (Catálogo)
    path('', views.home, name='home'),
    
    # Chat e Mensagens
    path('enviar-mensagem/', views.enviar_mensagem, name='enviar_mensagem'),
    
    # Ações do ADM (Liberar preço após a conversa)
    path('pedido/liberar/<int:pedido_id>/', views.liberar_para_carrinho, name='liberar_para_carrinho'),
    
    # Frete e Checkout (Para o cliente)
    path('pedido/frete/<int:pedido_id>/', views.calcular_frete, name='calcular_frete'),
    path('pedido/pagar/<int:pedido_id>/', views.finalizar_pagamento, name='finalizar_pagamento'),
    
    # Telas de retorno do Mercado Pago (Crie os HTMLs sucesso.html e erro.html depois)
    path('sucesso/', lambda request: render(request, 'sucesso.html'), name='sucesso'),
    path('erro/', lambda request: render(request, 'erro.html'), name='erro'),
    path('perfil/', views.editar_perfil, name='editar_perfil'),
    
    # Atualização do catálogo via AJAX
    path('catalogo-atualizado/', views.catalogo_atualizado, name='catalogo_atualizado'),
]