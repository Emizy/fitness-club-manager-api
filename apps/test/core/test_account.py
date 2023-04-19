import pytest
from faker import Faker
from utils.enums import MembershipEnum
from apps.test.endpoints import EndPoint

fake = Faker()


@pytest.mark.django_db
class TestAccount:
    def test_user_create_account_success(self, client):
        payload = {
            "name": fake.name(),
            "email": 'test@example.com',
            "phone_number": "08034956622"

        }
        response = client.post(f'{EndPoint.USER_ENDPOINT}/', payload, format='json')
        assert response.status_code == 201
        data = response.data
        assert payload.get('name') == data['data']['name']
        assert payload.get('email') == data['data']['email']
        assert payload.get('phone_number') == data['data']['phone_number']

    def test_user_create_account_fail(self, client):
        """
        This test case handle testing if serializer validation for each field is working
        """
        payload = {"name": fake.name(),
                   "email": "",
                   "phone_number": ""}
        response = client.post(f'{EndPoint.USER_ENDPOINT}/', payload, format='json')
        assert response.status_code == 400
        data = response.data
        assert 'errors' in data
        errors = data.get('errors')
        assert 'This field may not be blank.' in errors.values()

    def test_user_create_account_email_already_exist(self, client):
        """
        This test case handle testing the uniqueness of email
        """
        payload = {
            "name": fake.name(),
            "email": 'johndoe@example.com'
        }
        response = client.post(f'{EndPoint.USER_ENDPOINT}/', payload, format='json')
        assert response.status_code == 201
        new_payload = {
            "name": fake.name(),
            "email": 'johndoe@example.com'
        }
        _response = client.post(f'{EndPoint.USER_ENDPOINT}/', new_payload, format='json')
        assert _response.status_code == 400
        data = _response.data
        assert 'message' in data
        assert 'Email already exist' == data.get('message')


@pytest.mark.django_db
class TestMemberShip:
    def test_list_membership(self, client, setup_user_account):
        """
        this test if the membership for the user existed
        """
        user = setup_user_account
        response = client.get(f'{EndPoint.MEMBERSHIP_ENDPOINT}/')
        data = response.data
        assert response.status_code == 200
        results = response.data['data']['results']
        membership_exist = list(filter(lambda x: x.get('id') == user['membership']['id'], results))
        assert len(membership_exist) > 0

    def test_cancel_membership(self, client, setup_user_account):
        """
        this test if membership cancellation request and assert if the request was successful
        """
        user = setup_user_account
        response = client.put(f'{EndPoint.MEMBERSHIP_ENDPOINT}/{user["membership"]["id"]}/cancel/')
        assert response.status_code == 204

        # call get membership detail endpoint to retrieve the membership and check if data is correctly cancelled
        _response = client.get(f'{EndPoint.MEMBERSHIP_ENDPOINT}/{user["membership"]["id"]}/')
        assert _response.status_code == 200
        data = _response.data['data']
        assert data['state'] == MembershipEnum.CANCELLED


@pytest.mark.django_db
class TestFitnessClub:
    def test_create_fitness_club(self, client):
        """
        this test handle test creating fitness club
        """
        payload = {
            "name": fake.name(),
            "description": fake.sentence()
        }
        response = client.post(f'{EndPoint.FITNESS_CLUB_ENDPOINT}/', payload, format='json')
        assert response.status_code == 201
        data = response.data['data']
        assert data.get('name') == payload['name']
        assert data.get('description') == payload['description']

    def test_listing_fitness_club(self, client, setup_fitness_club):
        """
        this test the listing of fitness club endpoint
        """
        clubs = setup_fitness_club
        response = client.get(f'{EndPoint.FITNESS_CLUB_ENDPOINT}/')
        assert response.status_code == 200
        results = response.data['data']['results']
        assert len(results) == len(clubs)


@pytest.mark.django_db
class TestCheckIn:
    def test_if_user_can_checkin_correctly(self, client, setup_user_account, setup_fitness_club):
        """
        This endpoint test if user can check in if all criteria is being meant
        """
        user = setup_user_account
        clubs = setup_fitness_club
        payload = {
            'user': user['id'],
            'club': clubs[0]['id']
        }
        response = client.post(f'{EndPoint.CHECKIN_ENDPOINT}/', payload, format='json')
        assert response.status_code == 201
        data = response.data
        assert 'Checkin successful' == data['message']

    def test_if_credit_get_deducted_if_checkin_is_successful(self, client, setup_user_account, setup_fitness_club):
        """
        This endpoint test if user membership credit get deducted by 1 if checkin was successful
        """
        user = setup_user_account
        clubs = setup_fitness_club
        payload = {
            'user': user['id'],
            'club': clubs[0]['id']
        }
        response = client.post(f'{EndPoint.CHECKIN_ENDPOINT}/', payload, format='json')
        assert response.status_code == 201
        # call membership endpoint to retrieve the updated data and validate
        response = client.get(f'{EndPoint.MEMBERSHIP_ENDPOINT}/{user["membership"]["id"]}/')
        assert response.status_code == 200
        data = response.data['data']
        current_wallet_credit = data['amount_of_credit']
        target_credit = current_wallet_credit - 1
        # make new checkin request since invoice already exist
        _payload = {
            'user': user['id'],
            'club': clubs[0]['id']
        }
        _ = client.post(f'{EndPoint.CHECKIN_ENDPOINT}/', _payload, format='json')
        # retrieve the current membership information and compare with the target credit
        response = client.get(f'{EndPoint.MEMBERSHIP_ENDPOINT}/{user["membership"]["id"]}/')
        data = response.data['data']
        assert int(target_credit) == int(data.get('amount_of_credit'))

    def test_fail_checkin_if_credit_is_zero(self, client, setup_user_account_with_zero_credit, setup_fitness_club):
        """
        this endpoint test check in failed when the membership credit is 0
        """
        user = setup_user_account_with_zero_credit
        clubs = setup_fitness_club
        payload = {
            'user': user.id,
            'club': clubs[0]['id']
        }
        response = client.post(f'{EndPoint.CHECKIN_ENDPOINT}/', payload, format='json')
        assert response.status_code == 400
        assert 'You currently do not credit in your membership wallet' == response.data['message']

    def test_fail_checkin_if_membership_end_date_has_elapse(self, client, setup_fitness_club,
                                                            setup_user_account_with_elapse_end_date):
        """
                this endpoint test check in failed when the membership credit is 0
                """
        user = setup_user_account_with_elapse_end_date
        clubs = setup_fitness_club
        payload = {
            'user': user.id,
            'club': clubs[0]['id']
        }
        response = client.post(f'{EndPoint.CHECKIN_ENDPOINT}/', payload, format='json')
        assert response.status_code == 400
        assert 'Your membership has expired' == response.data['message']

    def test_fail_checkin_if_membership_has_been_cancelled(self, client, setup_user_account, setup_fitness_club):
        """
        this endpoint test check in fail when a user tried to checkin with a cancelled membership account
        """
        user = setup_user_account
        clubs = setup_fitness_club
        # call cancel endpoint to cancel user membership
        user = setup_user_account
        response = client.put(f'{EndPoint.MEMBERSHIP_ENDPOINT}/{user["membership"]["id"]}/cancel/')
        assert response.status_code == 204
        payload = {
            'user': user['id'],
            'club': clubs[0]['id']
        }
        response = client.post(f'{EndPoint.CHECKIN_ENDPOINT}/', payload, format='json')
        assert response.status_code == 400
        data = response.data
        assert 'Your membership is already cancelled' == data['message']
