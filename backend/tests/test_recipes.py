import pytest


class TestRecipesApi:
    url_recipes = '/api/recipes/'
    url_recipe = '/api/recipes/{}/'

    @pytest.mark.django_db(transaction=True)
    def test_recipes_list(self, client, recipe):
        url = self.url_recipes
        response = client.get(url)
        code_expected = 200
        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе от неавторизированного пользователя '
            f'на `{url}` без параметров, возвращается код {code_expected}'
        )
        response_data = response.json()
        fields_in_response = ('count', 'next', 'previous', 'results')
        for field in fields_in_response:
            assert field in response_data.keys(), (
                f'Убедитесь, что при запросе `{url}`, '
                f' в ответе возвращается код {code_expected} с ключами '
                f'{fields_in_response}. Убедитесь, что пагинация включена'
            )
        expected_recipe_fields = (
            'id',
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        for field in expected_recipe_fields:
            assert field in response_data['results'][0].keys(), (
                f'Проверьте, что при GET запросе на `{url}`, '
                f'объект списка рецептов содержит поле {field}'
            )

    @pytest.mark.django_db(transaction=True)
    def test_get_recipe(self, client, recipe):
        url = self.url_recipe.format(recipe.id)
        response = client.get(url)
        code_expected = 200
        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе от неавторизированного пользователя '
            f'на `{url}` без параметров, возвращается код {code_expected}'
        )
        response_data = response.json()
        expected_recipe_fields = (
            'id',
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        for field in expected_recipe_fields:
            assert field in response_data.keys(), (
                f'Проверьте, что при GET запросе на `{url}`, '
                f'возвращаемый словарь содержит поле {field}'
            )
