import pytest

from .conftest import USER_REG_DATA


class TestUserApi:
    url_users = '/api/users/'
    url_me = '/api/users/me/'
    url_set_password = '/api/users/set_password/'

    @pytest.mark.django_db(transaction=True)
    def test_users_list(self, client):
        """ Тестирование эндпоинта всех пользователей"""
        url = self.url_users
        response = client.get(url)
        code_expected = 200
        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе от неавторизированного пользователя '
            f'`{url}` без параметров, возвращается код {code_expected}'
        )
        fields_in_response = ['count', 'next', 'previous', 'results']
        for field in fields_in_response:
            assert field in response.json().keys(), (
                f'Убедитесь, что при запросе `{url}`, '
                f'в ответе возвращается код {code_expected} с ключами '
                f'{fields_in_response}'
            )

    @pytest.mark.django_db(transaction=True)
    def test_reg_invalid_request_data(self, client):
        """
        Тестирование эндпоинта регистрации
        с невалидными данными.
        """
        url = self.url_users
        response = client.post(url)
        code_expected = 400
        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе `{url}` без параметров, '
            f'возвращается код {code_expected}'
        )
        fields_invalid = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        for field in fields_invalid:
            assert field in response.json().keys(), (
                f'Убедитесь, что при запросе `{url}` без параметров, '
                f'возвращается код {code_expected} с сообщением о том, '
                'при обработке каких полей возникла ошибка.'
                f'Не найдено поле {field}'
            )

    @pytest.mark.django_db(transaction=True)
    def test_reg_valid_request_data(self, client):
        """
        Тестирование эндпоинта регистрации
        с валидными данными.
        """
        url = self.url_users
        data = {
            'email': 'test3@test.ru',
            'username': 'TestUser3',
            'password': '12pdmRjfipr9',
            'first_name': 'Test',
            'last_name': 'Test'
        }
        response = client.post(url, data=data)
        code_expected = 201
        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе `{url}` с валидными параметрами, '
            f'возвращается код {code_expected}'
        )
        assert 'id' in response.data.keys(), (
            'Убедитесь, что после создания пользователя '
            'возвращается информация о его id'
        )
        data['id'] = response.data.get('id')
        data.pop('password')
        assert response.data == data, (
            'Убедитесь, что после создания пользователя '
            'возвращаются корректные данные о нем'
        )

    @pytest.mark.django_db(transaction=True)
    def test_me_endpoint_not_auth(self, client):
        """
        Тестирование эндпоинта с информацией
        о себе без аутентификации.
        """
        url = self.url_me
        response = client.get(url)
        code_expected = 401
        assert response.status_code == code_expected, (
            f'Проверьте, что при GET запросе `{url}` без токена '
            f'авторизации возвращается статус {code_expected}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_me_endpoint_valid_data(self, user_client, user_data_me):
        """
        Тестирование эндпоинта с информацией
        о себе с аутентификацией.
        """
        url = self.url_me
        response = user_client.get(url)
        code_expected = 200
        assert response.status_code == code_expected, (
            f'Проверьте, что при GET запросе `{url}` с токеном авторизации '
            f'возвращается статус {code_expected}'
        )
        for key_response, value_response in response.data.items():
            assert user_data_me.get(key_response) == value_response, (
                'Убедитесь, что при запросе информации о себе '
                'возвращаются корректные данные'
            )

    @pytest.mark.django_db(transaction=True)
    def test_user_information_endpoint_not_auth(self, client, user_2):
        """
        Тестирование эндпоинта с информацией
        о пользователи без аутентификации.
        """
        url = f'/api/users/{user_2.id}/'
        response = client.get(url)
        code_expected = 401
        assert response.status_code == code_expected, (
            f'Проверьте, что при GET запросе `{url}` без токена '
            f'авторизации возвращается статус {code_expected}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_user_information_endpoint_invalid_data(self, user_client):
        """
        Тестирование эндпоинта с информацией
        о несуществующем пользователи.
        """
        url = '/api/users/1111/'
        response = user_client.get(url)
        code_expected = 404
        assert response.status_code == code_expected, (
            f'Проверьте, что при GET запросе несуществующего '
            f'пользователя возвращается статус {code_expected}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_user_information_endpoint_auth(
        self,
        user_client,
        user_2,
        user_2_data
    ):
        """
        Тестирование эндпоинта с информацией
        о пользователи с аутентификацией.
        """
        url = f'/api/users/{user_2.id}/'
        response = user_client.get(url)
        code_expected = 200
        assert response.status_code == code_expected, (
            f'Проверьте, что при GET запросе `{url}` c токеном '
            f'авторизации возвращается статус {code_expected}'
        )
        for key_response, value_response in response.data.items():
            assert user_2_data.get(key_response) == value_response, (
                'Убедитесь, что при запросе информации о себе '
                'возвращаются корректные данные'
            )

    @pytest.mark.django_db(transaction=True)
    def test_set_password_not_auth(self, client):
        """Тестирование эндпоинта для смены пароля без токена."""
        url = self.url_set_password
        response = client.post(url)
        code_expected = 401
        assert response.status_code == code_expected, (
            f'Проверьте, что при POST запросе `{url}` без токена '
            f'авторизации возвращается статус {code_expected}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_set_password_invalid_data(self, user_client):
        """Тестирование эндпоинта для смены пароля с невалидными данными"""
        url = self.url_set_password
        response = user_client.post(url)
        code_expected = 400
        assert response.status_code == code_expected, (
            f'Проверьте, что при POST запросе `{url}` c '
            f'невалидными данными возвращается статус {code_expected}'
        )
        fields_invalid = ('new_password', 'current_password')
        for field in fields_invalid:
            assert field in response.json().keys(), (
                f'Убедитесь, что при запросе `{url}` без параметров, '
                f'возвращается код {code_expected} с сообщением о том, '
                'при обработке каких полей возникла ошибка.'
                f'Не найдено поле {field}'
            )

    @pytest.mark.django_db(transaction=True)
    def test_set_password_valid_data(self, user_client):
        """Тестирование эндпоинта для смены пароля с валидными данными"""
        url = self.url_set_password
        data = {
            'new_password': 'coeo094njvo0',
            'current_password': USER_REG_DATA['password']
        }
        response = user_client.post(url, data=data)
        code_expected = 204
        assert response.status_code == code_expected, (
            f'Проверьте, что при POST запросе `{url}` c '
            f'валидными данными возвращается статус {code_expected}'
        )
        assert response.data == data, (
            'Убедитесь, что при изменении пароля '
            'возвращаются корректные данные'
        )
