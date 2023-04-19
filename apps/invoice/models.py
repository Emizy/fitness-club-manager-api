from django.db import models

from apps.core.models import User
from utils.enums import InvoiceStateEnum
from utils.membership import MembershipAbstract


class Invoice(MembershipAbstract):
    """
    Invoice holds all the invoice generated for a particular membership
    """
    status = models.CharField(max_length=20, choices=InvoiceStateEnum.choices(), default=InvoiceStateEnum.PAID)
    date = models.DateField(null=False, blank=False)
    description = models.TextField(default='')
    amount = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.membership.user.name} | {self.amount}"

    class Meta:
        db_table = 'invoice'
        verbose_name_plural = 'Invoices'


class InvoiceRow(models.Model):
    """
    Contain the invoice line for an invoice
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='rows')
    amount = models.FloatField(default=0.0)
    description = models.TextField(default='')

    def __str__(self):
        return f"Invoice: {self.invoice.id} | {self.amount}"

    class Meta:
        db_table = 'invoice_row'
        verbose_name_plural = 'Invoice Rows'
