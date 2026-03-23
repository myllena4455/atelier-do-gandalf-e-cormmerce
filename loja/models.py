from django.db import models
from django.contrib.auth.models import User

# Perfil do Cliente (Endereço, CPF e Telefone)
class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='perfis/', blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True)
    telefone = models.CharField(max_length=15, blank=True)
    endereco = models.TextField(blank=True)
    cep = models.CharField(max_length=9, blank=True)
    is_adm = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

# Produto do Catálogo
class Produto(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    preco_base = models.DecimalField(max_digits=10, decimal_places=2)
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

# Até 5 fotos por produto
class ImagemProduto(models.Model):
    produto = models.ForeignKey(Produto, related_name='imagens', on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='produtos/')

# O "Coração" da venda personalizada
class Pedido(models.Model):
    STATUS_CHOICES = [
        ('negociacao', 'Em Negociação'),
        ('liberado', 'Liberado para Carrinho'),
        ('pago', 'Pago'),
        ('cancelado', 'Cancelado'),
    ]
    
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    valor_personalizado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='negociacao')
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.cliente.username}"

# Mensagens do Chat com suporte a Foto/Vídeo
class MensagemChat(models.Model):
    remetente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enviadas')
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recebidas')
    texto = models.TextField(blank=True)
    arquivo = models.FileField(upload_to='chat/', blank=True, null=True)
    data_envio = models.DateTimeField(auto_now_add=True)