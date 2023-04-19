import pytest
from faker import Faker
from apps.core.models import MemberShip
from utils.base import InvoiceManager
from apps.invoice.models import Invoice, InvoiceRow

fake = Faker()


@pytest.mark.django_db
class TestInvoiceManager:
    def test_if_invoice_manager_created_new_invoice(self, setup_user_account):
        """
        Method test if new invoice is being created when create method is called inside invoice manager
        """
        user = setup_user_account
        membership = MemberShip.objects.get(id=user['membership']['id'])
        invoice_manager = InvoiceManager(membership, **{'amount': 100})
        invoice = invoice_manager.create_invoice()
        # assert an invoice exist inside db
        assert Invoice.objects.all().count() > 0



