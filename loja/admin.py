from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Produto, ImagemProduto, Perfil

class ImagemInline(admin.TabularInline):
    model = ImagemProduto
    extra = 5

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    inlines = [ImagemInline]

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Mostrar primeiro os ADMs
        return qs.order_by('-is_staff', 'username')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Perfil)

