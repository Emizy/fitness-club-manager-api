import pytest

from apps.test.endpoints import EndPoint
from utils.enums import InvoiceStateEnum


@pytest.mark.django_db
class TestInvoice:
    def test_list_all_invoice(self, client, setup_invoice):
        """
            test invoice listing if the already created invoice exist inside the list returned
        """
        invoice = setup_invoice
        response = client.get(f'{EndPoint.INVOICE_ENDPOINT}/')
        assert response.status_code == 200
        results = response.data['data']['results']
        invoice_exist = list(filter(lambda x: x.get('id') == invoice['id'], results))
        assert len(invoice_exist) > 0

    def test_create_invoice(self, client, setup_user_account):
        """
        this method test invoice create endpoint and assert if the right amount is being updated inside the db
        """
        user = setup_user_account
        payload = {
            'membership': user['membership']['id'],
            'amount': 1000
        }
        response = client.post(f'{EndPoint.INVOICE_ENDPOINT}/', payload, format='json')
        assert response.status_code == 201
        data = response.data['data']
        # make request to get invoice endpoint
        response = client.get(f'{EndPoint.INVOICE_ENDPOINT}/{data["id"]}/')
        assert response.status_code == 200
        _data = response.data['data']
        assert _data['amount'] == payload['amount']

    def test_add_invoice_row(self, client, setup_invoice):
        """
        this test add invoice row endpoint
        """
        invoice = setup_invoice
        payload = {
            'amount': 200,
            'description': 'Test invoice row'
        }
        response = client.put(f'{EndPoint.INVOICE_ENDPOINT}/{invoice["id"]}/add_row/', payload, format='json')
        assert response.status_code == 200
        data = response.data['data']
        assert data['amount'] == payload['amount']
        assert data['description'] == payload['description']

    def test_void_invoice(self, client, setup_invoice):
        """
        this method test if invoice is correctly voided
        """
        invoice = setup_invoice
        response = client.put(f'{EndPoint.INVOICE_ENDPOINT}/{invoice["id"]}/void/')
        assert response.status_code == 204

        # fetch the invoice from the endpoint and assert if its truly void
        response = client.get(f'{EndPoint.INVOICE_ENDPOINT}/{invoice["id"]}/')
        assert response.status_code == 200
        data = response.data['data']
        assert data['status'] == InvoiceStateEnum.VOID

    def test_delete_invoice(self, client, setup_invoice):
        """
        this endpoint deleting of an invoice
        """
        invoice = setup_invoice
        response = client.delete(f'{EndPoint.INVOICE_ENDPOINT}/{invoice["id"]}/')
        assert response.status_code == 204

        # fetch the invoice from the endpoint and assert if its exist based on status_code
        response = client.get(f'{EndPoint.INVOICE_ENDPOINT}/{invoice["id"]}/')
        assert response.status_code == 400
