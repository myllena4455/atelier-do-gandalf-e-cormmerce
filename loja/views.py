import os
import requests
import mercadopago
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from .models import Produto, Pedido, MensagemChat, Perfil
from .forms import PerfilForm


# Inicializa o SDK do Mercado Pago usando o Token do seu .env
sdk = mercadopago.SDK(settings.MERCADO_PAGO_TOKEN)

# 1. HOME / CATÁLOGO
def home(request):
    produtos = Produto.objects.all()
    # Passamos a Public Key para o Front-end conseguir carregar o checkout
    context = {
        'produtos': produtos,
        'public_key': os.getenv('MERCADO_PAGO_PUBLIC_KEY')
    }
    return render(request, 'index.html', context)

# 2. CHAT E NEGOCIAÇÃO (Envio de texto, fotos e vídeos)
def enviar_mensagem(request):
    if request.method == 'POST':
        texto = request.POST.get('texto')
        arquivo = request.FILES.get('arquivo') # Cloudinary recebe isso automaticamente
        destinatario_id = request.POST.get('destinatario_id')
        destinatario = get_object_or_404(Perfil, id=destinatario_id).user

        nova_msg = MensagemChat.objects.create(
            remetente=request.user,
            destinatario=destinatario,
            texto=texto,
            arquivo=arquivo
        )
        return JsonResponse({'status': 'ok', 'msg_id': nova_msg.id, 'url': nova_msg.arquivo.url if nova_msg.arquivo else ''})

# 3. AÇÃO DO ADM: AJUSTAR PREÇO E LIBERAR PARA CARRINHO
def liberar_para_carrinho(request, pedido_id):
    if not request.user.is_staff:
        return JsonResponse({'erro': 'Acesso negado'}, status=403)
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    # O ADM envia o valor final negociado via POST
    valor_final = request.POST.get('valor_personalizado')
    
    pedido.valor_personalizado = valor_final
    pedido.status = 'liberado' # Muda o status para o cliente poder calcular frete
    pedido.save()
    return redirect('painel_adm')

# 4. CÁLCULO DE FRETE (MELHOR ENVIO)
def calcular_frete(request, pedido_id):
    if request.method == 'POST':
        cep_destino = request.POST.get('cep').replace('-', '')
        pedido = get_object_or_404(Pedido, id=pedido_id)
        
        url = f"{os.getenv('MELHOR_ENVIO_URL')}/api/v2/me/shipment/calculate"
        headers = {
            "Authorization": f"Bearer {os.getenv('MELHOR_ENVIO_TOKEN')}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Dados simplificados para cálculo (ajuste conforme seu produto)
        payload = {
            "from": {"postal_code": "54450040"}, # Seu CEP (Curado/Recife)
            "to": {"postal_code": cep_destino},
            "products": [{"id": "1", "quantity": 1, "weight": 0.5}] 
        }

        response = requests.post(url, json=payload, headers=headers)
        dados = response.json()

        # Pegamos a primeira opção de frete disponível
        if dados and isinstance(dados, list):
            valor_frete = dados[0].get('price', 0)
            pedido.valor_frete = valor_frete
            pedido.save()
            return JsonResponse({'frete': valor_frete, 'total': float(pedido.valor_personalizado) + float(valor_frete)})
        
        return JsonResponse({'erro': 'Não foi possível calcular o frete'}, status=400)

# 5. PAGAMENTO FINAL (MERCADO PAGO)
def finalizar_pagamento(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # O valor total é a soma do preço personalizado pelo ADM + o frete escolhido
    total_compra = float(pedido.valor_personalizado) + float(pedido.valor_frete)
    
    preference_data = {
        "items": [
            {
                "title": f"Atelier do Gandalf - Pedido #{pedido.id}",
                "quantity": 1,
                "unit_price": total_compra,
            }
        ],
        "back_urls": {
            "success": "http://127.0.0.1:8000/sucesso",
            "failure": "http://127.0.0.1:8000/erro",
            "pending": "http://127.0.0.1:8000/pendente"
        },
        "auto_return": "approved",
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]
    
    # Redireciona o cliente para a tela oficial de pagamento do Mercado Pago
    return redirect(preference["init_point"])


def editar_perfil(request):
    # Tenta pegar o perfil do usuário logado, se não existir, cria um novo
    perfil, created = Perfil.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PerfilForm(instance=perfil)
    
    return render(request, 'perfil.html', {'form': form})

# View para atualizar catálogo via AJAX
def catalogo_atualizado(request):
    produtos = Produto.objects.filter(disponivel=True)
    return render(request, 'catalogo_partial.html', {'produtos': produtos})