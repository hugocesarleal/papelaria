from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from estoque.models import ItemEstoque

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_admin',)}),  # Adiciona o campo `is_admin` no admin
    )

admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(ItemEstoque)
class ItemEstoqueAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade', 'valor')
    search_fields = ('nome',)
    list_editable = ('quantidade', 'valor')