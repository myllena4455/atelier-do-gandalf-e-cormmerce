from django.urls import path
from django.shortcuts import render
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    path('enviar-mensagem/', views.enviar_mensagem, name='enviar_mensagem'),
    path('chat/atualizar-orcamento/', views.atualizar_orcamento, name='atualizar_orcamento'),
    path('chat/mensagens-adm/', views.mensagens_adm, name='mensagens_adm'),
    path('chat/conversa/<int:cliente_id>/', views.carregar_conversa, name='carregar_conversa'),

    path('pedido/liberar/<int:pedido_id>/', views.liberar_para_carrinho, name='liberar_para_carrinho'),
    
    path('pedido/frete/<int:pedido_id>/', views.calcular_frete, name='calcular_frete'),
    path('pedido/pagar/<int:pedido_id>/', views.finalizar_pagamento, name='finalizar_pagamento'),
    
    # Telas de retorno do Mercado Pago (Crie os HTMLs sucesso.html e erro.html depois)
    path('sucesso/', lambda request: render(request, 'sucesso.html'), name='sucesso'),
    path('erro/', lambda request: render(request, 'erro.html'), name='erro'),
    
    # Atualização do catálogo via AJAX
    path('catalogo-atualizado/', views.catalogo_atualizado, name='catalogo_atualizado'),
    alogo/', views.gerenciar_catalogo, name='gerenciar_catalogo'),
    path('criar-conta-adm/', views.criar_conta_adm, name='criar_conta_adm'),
    path('gerenciar-adms/', views.gerenciar_adms, name='gerenciar_adms'),
    path('remover-adm/<int:adm_id>/', views.remover_adm, name='remover_adm'),
]