from django.contrib import admin
from .models import Produto, ImagemProduto, Perfil

class ImagemInline(admin.TabularInline):
    model = ImagemProduto
    extra = 5 # Limita a 5 campos de foto no painel

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    inlines = [ImagemInline]

admin.site.register(Perfil)

