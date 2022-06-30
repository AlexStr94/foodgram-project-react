import pytest
from users.models import Subscription


class TestSubscriptionsApi:
    url_subscribe = '/api/users/{}/subscribe/'
    url_subscriptions = '/api/users/subscriptions/'

    @pytest.mark.django_db(transaction=True)
    def test_subscribe_not_auth(self, client):
        """
        Проверка ответа при попытки
        подписаться/отписаться без токена
        """
        url = self.url_subscribe.format('1')
        response = client.post(url)
        code_expected = 401
        assert response.status_code == code_expected, (
            f'Убедитесь, что при POST запросе от неавторизированного  '
            f'пользователя`{url}` без параметров, возвращается '
            f'код {code_expected}'
        )
        response = client.delete(url)
        code_expected = 401
        assert response.status_code == code_expected, (
            f'Убедитесь, что при DELETE запросе от неавторизированного '
            f'пользователя`{url}` без параметров, возвращается '
            f'код {code_expected}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_subscribe_nonexists_user(self, user_client):
        """
        Проверка ответа при попытки подписаться/отписаться
        на/от несуществующего пользователя
        """
        url = self.url_subscribe.format('1111')
        response = user_client.post(url)
        code_expected = 404
        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе несуществующего пользователя '
            f'по `{url}` без параметров, возвращается код {code_expected}'
        )
        response = user_client.delete(url)
        code_expected = 404
        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе несуществующего пользователя '
            f'по `{url}` без параметров, возвращается код {code_expected}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_subscribe(self, user, user_client, user_2):
        """
        Проверка работоспособности эндпоинта
        подписки/отписки на/от другого пользователя
        """
        url = self.url_subscribe.format(user_2.id)
        response = user_client.post(url)
        code_expected = 201
        assert response.status_code == code_expected, (
            f'Убедитесь, что при обращении авторизированного пользователя '
            f'на эндпоинт подписки `{url}`, он получает ответ {code_expected}'
        )
        response_data = response.json()
        expected_fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
            )
        for field in expected_fields:
            assert field in response_data, (
                f'Проверьте, что при POST запросе на `{url}`, '
                f'объект списка содержит {field}'
            )
        subscription = Subscription.objects.filter(
            follower=user,
            user=user_2
        ).exists()
        assert subscription, (
            'Проверьте, что после обращения на эндпоинт подписки, '
            'она создается'
        )
        response = user_client.post(url)
        code_expected = 400
        assert response.status_code == code_expected, (
            f'Убедитесь, что при обращении авторизированного пользователя '
            f'на эндпоинт подписки `{url}`, нельзя подписаться повторно и '
            f'приходит ответ {code_expected}'
        )
        response = user_client.delete(url)
        code_expected = 204
        assert response.status_code == code_expected, (
            f'Убедитесь, что при попытки авторизированного пользователя '
            f'отписаться от другого пользователя посредством DELETE запроса '
            f'на эндпоинт подписки `{url}`, он получает ответ {code_expected}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_subscriptions_not_auth(self, client):
        """
        Проверка недоступности страницы подписок
        для неавторизированного пользователя
        """
        url = self.url_subscriptions
        response = client.get(url)
        code_expected = 401
        assert response.status_code == code_expected, (
            f'Убедитесь, что при обращении неавторизированного пользователя '
            f'на эндпоинт подписок `{url}`, он получает ответ {code_expected}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_subscriptions(self, user_client):
        url = self.url_subscriptions
        response = user_client.get(url)
        code_expected = 200
        assert response.status_code == code_expected, (
            f'Убедитесь, что при обращении авторизированного пользователя '
            f'на эндпоинт подписок `{url}`, он получает ответ {code_expected}'
        )
        fields_in_response = ('count', 'next', 'previous', 'results')
        for field in fields_in_response:
            assert field in response.json().keys(), (
                f'Убедитесь, что при запросе `{url}`, '
                f' в ответе возвращается код {code_expected} с ключами '
                f'{fields_in_response}'
            )
