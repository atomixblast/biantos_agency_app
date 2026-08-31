from django.contrib import admin

from .models import Order, Customer, SalesExecutive, Article, ArticleOrder, Payment

# Register your models here.

class ArticleOrderInline(admin.TabularInline):
    model = ArticleOrder
    extra = 0
    readonly_fields = ('article', 'qty', 'discount')


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('created_by', 'created_at')
    fields = ('amount', 'payment_date', 'payment_method', 'reference', 'notes', 'created_by', 'created_at')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer', 'sales_executive', 'state', 'total', 'created_at')
    list_filter = ('state', 'customer', 'sales_executive', 'created_at')
    search_fields = ('name', 'customer__name', 'sales_executive__name')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'total')
    inlines = [ArticleOrderInline, PaymentInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'state', 'ordered_at', 'state_date')
        }),
        ('Parties prenantes', {
            'fields': ('customer', 'sales_executive')
        }),
        ('Montants', {
            'fields': ('total', 'discount', 'cashed')
        }),
        ('Données techniques', {
            'fields': ('json_repr', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'tel', 'created_at')
    search_fields = ('name', 'tel')
    ordering = ('name',)


class SalesExecutiveAdmin(admin.ModelAdmin):
    list_display = ('name', 'tel', 'created_at')
    search_fields = ('name', 'tel')
    ordering = ('name',)


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('name', 'ref', 'sale_price', 'created_at')
    search_fields = ('name', 'ref')
    list_filter = ('created_at',)
    ordering = ('name',)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'payment_date', 'payment_method', 'reference', 'created_by', 'created_at')
    list_filter = ('payment_method', 'payment_date', 'created_at')
    search_fields = ('order__name', 'reference', 'notes')
    date_hierarchy = 'payment_date'
    ordering = ('-payment_date', '-created_at')
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Informations du paiement', {
            'fields': ('order', 'amount', 'payment_date', 'payment_method')
        }),
        ('Détails', {
            'fields': ('reference', 'notes')
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une création
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Order, OrderAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(SalesExecutive, SalesExecutiveAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Payment, PaymentAdmin)