from django.contrib import admin
from .models import CalculationHistory

@admin.register(CalculationHistory)
class CalculationHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'alpha', 'created_at')
    list_filter = ('user', 'created_at')
    readonly_fields = [field.name for field in CalculationHistory._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False