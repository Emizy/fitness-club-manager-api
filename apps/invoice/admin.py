from django.contrib import admin
from apps.invoice.models import Invoice, InvoiceRow


class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "status",
        "date",
        "description",
        "amount",
        "membership",
    )


class InvoiceRowAdmin(admin.ModelAdmin):
    list_display = (
        "invoice",
        "description",
        "amount",
    )


admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(InvoiceRow, InvoiceRowAdmin)
