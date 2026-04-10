import os
import requests
import mercadopago
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produto, Pedido, MensagemChat, Perfil, ImagemProduto
from .forms import PerfilForm


# Inicializa o SDK do Mercado Pago usando o Token do seu .env
sdk = mercadopago.SDK(settings.MERCADO_PAGO_TOKEN)

def home(request):
    produtos = Produto.objects.all()
    perfil = None
    if request.user.is_authenticated:
        perfil = Perfil.objects.filter(user=request.user).first()

    # Passamos a Public Key para o Front-end conseguir carregar o checkout
    context = {
        'produtos': produtos,
        'public_key': os.getenv('MERCADO_PAGO_PUBLIC_KEY'),
        'perfil': perfil,
    }
    return render(request, 'index.html', context)

def enviar_mensagem(request):
    if request.method == 'POST':
        texto = request.POST.get('texto')
        arquivo = request.FILES.get('arquivo')

        # Se o usuário é cliente (não staff), enviar para TODOS os ADMs
        if not request.user.is_staff:
            from django.contrib.auth.models import User
            adms = User.objects.filter(is_staff=True)
            
            mensagens_criadas = []
            for adm in adms:
                nova_msg = MensagemChat.objects.create(
                    remetente=request.user,
                    destinatario=adm,
                    texto=texto,
                    arquivo=arquivo
                )
                mensagens_criadas.append(nova_msg)
            
            if mensagens_criadas:
                return JsonResponse({
                    'status': 'ok', 
                    'msg_id': mensagens_criadas[0].id, 
                    'url': mensagens_criadas[0].arquivo.url if mensagens_criadas[0].arquivo else '',
                    'enviado_para_adms': len(mensagens_criadas)
                })
        else:
            
            destinatario_id = request.POST.get('destinatario_id')
            destinatario = get_object_or_404(Perfil, id=destinatario_id).user
            
            nova_msg = MensagemChat.objects.create(
                remetente=request.user,
                destinatario=destinatario,
                texto=texto,
                arquivo=arquivo
            )
            return JsonResponse({
                'status': 'ok', 
                'msg_id': nova_msg.id, 
                'url': nova_msg.arquivo.url if nova_msg.arquivo else ''
            })

    return JsonResponse({'erro': 'Método não permitido'}, status=405)

def liberar_para_carrinho(request, pedido_id):
    if not request.user.is_staff:
        return JsonResponse({'erro': 'Acesso negado'}, status=403)
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    valor_final = request.POST.get('valor_personalizado')
    
    pedido.valor_personalizado = valor_final
    pedido.status = 'liberado' # Muda o status para o cliente poder calcular frete
    pedido.save()
    return redirect('painel_adm')

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
            "from": {"postal_code": "54450040"}, # Seu CEP (Curado/Recife)
            "to": {"postal_code": cep_destino},
            "products": [{"id": "1", "quantity":
            "to": {"postal_code": cep_destino},
            "products": [{"id": "1", "quantity": 1, "weight": 0.5}]
        response = requests.post(url, json=payload, headers=headers)
        dados = response.json()

        # Pegamos a primeira opção de frete disponível
        if dados and isinstance(dados, list):
            pedido.valor_frete = valor_frete
            pedido.save()
            return JsonResponse({'frete': valor_frete, 'total': float(pedido.valor_personalizado) + float(valor_frete)})
        
        return JsonResponse({'erro': 'Não foi possível calcular o frete'}, status=400)

# 5. PAGAMENTO FINAL (MERCADO PAGO)
def finalizar_pagamento(request, pedido_id):
    
    # O valor total é a soma do preço personalizado pelo ADM + o frete escolhido
    total_compra = float(pedido.valor_personalizado) + float(pedido.valor_frete)
    
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

in_required
def editar_perfil(request):
    # Tenta pegar o perfil do usuário logado, se não existir, cria um novo
    perfil, created = Perfil.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
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

# 6. ATUALIZAR ORÇAMENTO (ADM)
@login_required
def atualizar_orcamento(request):
    if not request.user.is_staff:
        return JsonResponse({'erro': 'Acesso negado'}, status=403)
    if request.method == 'POST':
        venda_id = request.POST.get('venda_id')
        novo_preco = request.POST.get('novo_preco')
        
        try:
            pedido = Pedido.objects.get(id=venda_id)
            pedido.valor_personalizado = float(novo_preco)
            pedido.save()
            
            # Criar mensagem no chat informando a mudança
            MensagemChat.objects.create(
                remetente=request.user,
                destinatario=pedido.cliente,
                texto=f"ADM atualizou o preço para R$ {novo_preco}"
            )
            return JsonResponse({'status': 'ok', 'novo_preco': novo_preco})
        except Pedido.DoesNotExist:
            return JsonResponse({'erro': 'Pedido não encontrado'}, status=404)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

# 7. MENSAGENS DO ADM (VER TODAS AS CONVERSAS)
@login_required
# 7. MENSAGENS DO ADM (VER TODAS AS CONVERSAS DE TODOS OS CLIENTES)
@login_required
def mensagens_adm(request):
    if not request.user.is_staff:
    # Isso garante que todos os ADMs vejam todas as conversas de todos os clientes
    from django.contrib.auth.models import User
    adms = User.objects.filter(is_staff=True)
    mensagens = MensagemChat.objects.filter(destinatario__in=adms).order_by('-data_envio')
    
    # Agrupar por cliente para mostrar conversas organizadas
    conversas = {}
    for msg in mensagens:
            conversas[cliente_id] = {
                'cliente': msg.remetente,
                'mensagens': [],
                'ultima_msg': msg
            }
        conversas[cliente_id]['mensagens'].append(msg)
    # Ordenar conversas pela última mensagem
    conversas_ordenadas = sorted(
        conversas.values(), 
        key=lambda x: x['ultima_msg'].data_envio, 
        reverse=True
    )
    
    # Retornar dados para o frontend
    dados = []
    for conversa in conversas_ordenadas:
        dados.append({
            'cliente_nome': conversa['cliente'].username,
            'ultima_msg': conversa['ultima_msg'].texto[:50] + '...' if len(conversa['ultima_msg'].texto) > 50 else conversa['ultima_msg'].texto,
            'data': conversa['ultima_msg'].data_envio.strftime('%d/%m/%Y %H:%M'),
            'total_msgs': len(conversa['mensagens'])
        })
    
    return JsonResponse({'conversas': dados})
 CARREGAR MENSAGENS DE UMA CONVERSA ESPECÍFICA
@login_required
def carregar_conversa(request, cliente_id):
    if not request.user.is_staff:
        return JsonResponse({'erro': 'Acesso negado'}, status=403)
    
    try:
        from django.contrib.auth.models import User
        cliente = User.objects.get(id=cliente_id)
        adms = User.objects.filter(is_staff=True)
        
        
            remetente=cliente, 
            destinatario__in=adms
        )
        mensagens_adms_para_cliente = MensagemChat.objects.filter(
            remetente__in=adms, 
            destinatario=cliente
        )
        
        
        todas_mensagens = list(mensagens_cliente_para_adms) + list(mensagens_adms_para_cliente)
        todas_mensagens.sort(key=lambda x: x.data_envio)
        
        
        mensagens_formatadas = []
        for msg in todas_mensagens:
            mensagens_formatadas.append({
                'id': msg.id,
                'remetente': msg.remetente.username,
                'remetente_id': msg.remetente.id,
                'is_adm': msg.remetente.is_staff,
                'texto': msg.texto,
                'arquivo_url': msg.arquivo.url if msg.arquivo else None,
                'data_envio': msg.data_envio.strftime('%d/%m/%Y %H:%M:%S')
            })
        
        return JsonResponse({
            'cliente_nome': cliente.username,
            'mensagens': mensagens_formatadas
        })
        
    except User.DoesNotExist:
        return JsonResponse({'erro': 'Cliente não encontrado'}, status=404)


@login_required
def gerenciar_catalogo(request):
    if not request.user.is_staff:
        return redirect('home')
    
    if request.method == 'POST':
        if 'adicionar_produto' in request.POST:
            
            nome = request.POST.get('nome')
            descricao = request.POST.get('descricao')
            preco = request.POST.get('preco')
            
            if nome and preco:
                produto = Produto.objects.create(
                    nome=nome,
                    descricao=descricao,
                    preco_base=float(preco)
                )
                
                # Processar imagens
                imagens = request.FILES.getlist('imagens')
                for imagem in imagens[:5]:  # Máximo 5 imagens
                    ImagemProduto.objects.create(produto=produto, imagem=imagem)
                
                messages.success(request, f'Produto "{nome}" adicionado com sucesso!')
        
        elif 'editar_produto' in request.POST:
            
            produto_id = request.POST.get('produto_id')
            try:
                produto.nome = request.POST.get('nome', produto.nome)
                produto.descricao = request.POST.get('descricao', produto.descricao)
                produto.preco_base = float(request.POST.get('preco', produto.preco_base))
                produto.disponivel = 'disponivel' in request.POST
                produto.save()
                
                # Adicionar novas imagens se enviadas
                novas_imagens = request.FILES.getlist('novas_imagens')
                for imagem in novas_imagens[:5 - produto.imagens.count()]:
                    ImagemProduto.objects.create(produto=produto, imagem=imagem)
                
                messages.success(request, f'Produto "{produto.nome}" atualizado!')
            except Produto.DoesNotExist:
                messages.error(request, 'Produto não encontrado.')
        
        elif 'remover_produto' in request.POST:
            # Remover produto
            produto_id = request.POST.get('produto_id')
            try:produto = Produto.objects.get(id=produto_id)
                nome = produto.nome
                produto.delete()
                messages.success(request, f'Produto "{nome}" removido!')
            except Produto.DoesNotExist:
                messages.error(request, 'Produto não encontrado.')
        
        return redirect('gerenciar_catalogo')
    
    # GET -  = Produto.objects.all().order_by('-id')
    return render(request, 'gerenciar_catalogo.html', {'produtos': produtos})

# 10. CRIAR CONTA ADM (APENAS ADM EXISTENTE)
@login_required
def criar_conta_adm(request):
    if not request.user.is_staff:
        return redirect('home')
    
    if request.method == 'POST':
        from django.contrib.auth.models import User
        
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('criar_conta_adm')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Nome de usuário já existe.')
            return redirect('criar_conta_adm')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email já cadastrado.')
            return redirect('criar_conta_adm')
        
        # Criar novo ADM
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True
        )
        
        # Criar perfil
        Perfil.objects.create(
            user=user,
            cpf=request.POST.get('cpf', ''),
            telefone=request.POST.get('telefone', ''),
            endereco=request.POST.get('endereco', ''),
            cep=request.POST.get('cep', '00000-000')
        )
        
        messages.success(request, f'Conta ADM criada com sucesso para {username}!')
        return redirect('gerenciar_adms')
    rn render(request, 'criar_conta_adm.html')

# 11. GERENCIAR CONTAS ADM
@login_required
def gerenciar_adms(request):
    if not request.user.is_staff:
        return redirect('home')
    
    from django.contrib.auth.models import User
    from django.db.models import Count
    from datetime import date
    
    adms = User.objects.filter(is_staff=True).order_by('username')
    total_produtos = Produto.objects.count()
    
    return render(request, 'gerenciar_adms.html', {
        'adms': adms,
        'total_produtos': total_produtos,
        'mensagens_hoje': mensagens_hoje
    })

# 12. REMOVER CONTA ADM
@login_required
def remover_adm(request, adm_id):
    if not request.user.is_staff:
        return redirect('home')
    
    from django.contrib.auth.models import User
    
    try:
        adm = User.objects.get(id=adm_id, is_staff=True)
        
        if adm == request.user:
            messages.error(request, 'Você não pode remover sua própria conta ADM.')
            return redirect('gerenciar_adms')
        
        # Verificar se é o último ADM
        total_adms = User.objects.filter(is_staff=True).count()
        if total_adms <= 1:
            messages.error(request, 'Não é possível remover o último ADM do sistema.')
            return redirect('gerenciar_adms')
        
        nome = adm.username
        messages.success(request, f'Conta ADM "{nome}" removida com sucesso!')
        
    except User.DoesNotExist:
        messages.error(request, 'Conta ADM não encontrada.')
    
    return redirect('gerenciar_adms')