from django.contrib import admin

from target.models import Target


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ('name', 'metric', 'target_value', 'article', 'sales_executive', 'start_date', 'end_date')
    list_filter = ('metric', 'sales_executive', 'start_date')
    search_fields = ('name', 'article__name')
