import pytest


class TestIngredientsApi:
    url_ingredients = '/api/ingredients/'

    @pytest.mark.django_db(transaction=True)
    def test_ingredients_list(self, client, ingredient):
        url = self.url_ingredients
        response = client.get(url)
        code_expected = 200
        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе от неавторизированного пользователя '
            f'`{url}` без параметров, возвращается код {code_expected}'
        )

        response_data = response.json()
        assert type(response_data) == list, (
            f'Проверьте, что при GET запросе на `{url}`, '
            f'возвращается список без пагинации'
        )
        expected_fields = ('id', 'name', 'measurement_unit')
        for field in expected_fields:
            assert field in response_data[0], (
                f'Проверьте, что при GET запросе на `{url}`, '
                f'объект списка содержит {field}'
            )

    @pytest.mark.django_db(transaction=True)
    def test_ingredient(self, client, ingredient):
        url = f'{self.url_ingredients}{ingredient.id}/'
        response = client.get(url)
        code_expected = 200
        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе от неавторизированного пользователя '
            f'`{url}` без параметров, возвращается код {code_expected}'
        )

        response_data = response.json()
        expected_fields = ('id', 'name', 'measurement_unit')
        for field in expected_fields:
            assert field in response_data, (
                f'Проверьте, что при GET запросе на `{url}`, '
                f'объект списка содержит {field}'
            )
