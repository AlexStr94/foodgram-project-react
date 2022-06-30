import pytest

from .conftest import USER_REG_DATA


class TestAuthApi:
    url_get_token = '/api/auth/token/login/'
    url_destroy_token = '/api/auth/token/logout/'

    @pytest.mark.django_db(transaction=True)
    def test_get_token_valid_request_data(self, user_client):
        url = self.url_get_token
        data = {
            'email': USER_REG_DATA['email'],
            'password': USER_REG_DATA['password']
        }
        response = user_client.post(url, data=data)
        code_expected = 201
        assert response.status_code == code_expected, (
            f'Проверьте, что при POST запросе `{url}` c '
            f'валидными данными возвращается статус {code_expected}'
        )
        field = 'auth_token'
        assert field in response.json(), (
            f'Убедитесь, что при запросе `{url}` с валидным данными, '
            f'возвращается код {code_expected} и параметр auth_token'
        )

    @pytest.mark.django_db(transaction=True)
    def test_delete_token_not_auth(self, client):
        url = self.url_destroy_token
        response = client.post(url)
        code_expected = 401
        assert response.status_code == code_expected, (
            f'Проверьте, что при POST запросе `{url}`'
            f'от неавторизированного пользователя '
            f'возвращается статус {code_expected}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_delete_token_auth(self, user_client):
        url = self.url_destroy_token
        response = user_client.post(url)
        code_expected = 204
        assert response.status_code == code_expected, (
            f'Проверьте, что при POST запросе `{url}`'
            f'от авторизированного пользователя '
            f'возвращается статус {code_expected}'
        )
