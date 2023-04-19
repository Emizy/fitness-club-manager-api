import pytest
from faker import Faker
from datetime import datetime, timedelta
from rest_framework.test import APIClient
from apps.core.models import User, MemberShip
from utils.base import InvoiceManager
from apps.test.endpoints import EndPoint

fake = Faker()


@pytest.fixture
def client():
    """
    api client to be used as a fixture in making request to the endpoints
    """
    return APIClient()


@pytest.mark.django_db
@pytest.fixture
def setup_user_account(client):
    """
    This fixture handle setting up user account and membership by
    1.  Calling the user create endpoint
    """
    user_info = {
        "name": fake.name(),
        "email": fake.email(),
    }
    response = client.post(f'{EndPoint.USER_ENDPOINT}/', user_info, format='json')
    assert response.status_code == 201  # a fixture could also be use to validate endpoint test
    data = response.data
    return data.get('data')


@pytest.mark.django_db
@pytest.fixture
def setup_user_account_with_invoice(client):
    """
        This fixture handle setting up user
    """
    user_info = {
        "name": fake.name(),
        "email": fake.email(),
    }
    response = client.post(f'{EndPoint.USER_ENDPOINT}/', user_info, format='json')


@pytest.mark.django_db
@pytest.fixture
def setup_user_account_with_zero_credit(client):
    """
        This fixture handle setting up user membership account with zero credit
    """
    user_info = {
        "name": fake.name(),
        "email": fake.email(),
    }
    user = User.objects.create(**user_info)
    membership = MemberShip.objects.create(**{'user': user})
    invoice_manager = InvoiceManager(membership, **{'amount': 100})
    invoice = invoice_manager.create_invoice()
    # Update the membership credit back to zero in order to test checkin endpoint
    # for checkin denied for membership with zero credit
    _ = MemberShip.objects.filter(id=membership.id).update(amount_of_credit=0)
    return user


@pytest.mark.django_db
@pytest.fixture
def setup_user_account_with_elapse_end_date(client):
    """
        This fixture handle setting up user membership account with elapsed end date
    """
    user_info = {
        "name": fake.name(),
        "email": fake.email(),
    }
    user = User.objects.create(**user_info)
    membership = MemberShip.objects.create(**{'user': user})
    invoice_manager = InvoiceManager(membership, **{'amount': 100})
    _ = invoice_manager.create_invoice()
    # Update the membership end date 1 day back from the normal end date back to zero in order to test checkin endpoint
    # for checkin denied for membership with zero credit
    end_date = datetime.today().date() - timedelta(days=20)  # setting end date to 20 days
    # before today since invoice manager will set it to 30 days from today
    _ = MemberShip.objects.filter(id=membership.id).update(end_date=end_date)
    return user


@pytest.mark.django_db
@pytest.fixture
def setup_fitness_club(client):
    """
    Feature handles setting up fitness clubs inside the database
    """
    fitness_clubs = []
    for i in range(5):
        payload = {
            "name": fake.name(),
            "description": fake.sentence(),
        }
        response = client.post(f'{EndPoint.FITNESS_CLUB_ENDPOINT}/', payload, format='json')
        assert response.status_code == 201
        fitness_clubs.append(response.data['data'])
    return fitness_clubs


@pytest.mark.django_db
@pytest.fixture
def setup_invoice(client, setup_user_account):
    """
    setup test invoice inside the db
    """
    user = setup_user_account
    payload = {
        'membership': user['membership']['id'],
        'amount': 1000
    }
    response = client.post(f'{EndPoint.INVOICE_ENDPOINT}/', payload, format='json')
    assert response.status_code == 201
    return response.data['data']
