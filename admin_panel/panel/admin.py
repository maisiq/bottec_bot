from django.contrib import admin

from .models import Category, Product, Promo, Subcategory, User, UserBot


@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {
        'slug': ['name'],
    }


@admin.register(Subcategory)
class AdminSubcategory(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_select_related = ['category']
    prepopulated_fields = {
        'slug': ['name'],
    }


@admin.register(Product)
class AdminProduct(admin.ModelAdmin):
    list_display = ['name', 'price', 'subcategory']
    list_select_related = ['subcategory']


@admin.register(Promo)
class AdminPromo(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'active', 'last_succeeded_at']


@admin.register(User)
class AdminUser(admin.ModelAdmin):
    list_display = ['username', 'email']


@admin.register(UserBot)
class AdminCustomer(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'is_admin', 'is_staff']
