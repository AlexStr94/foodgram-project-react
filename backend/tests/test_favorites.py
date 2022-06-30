import pytest
from recipes.models import FavoriteRecipe


class TestFavoritesApi:
    url_favorite = '/api/recipes/{}/favorite/'

    @pytest.mark.django_db(transaction=True)
    def test_add_recipe_to_favorite_not_auth(self, recipe, client):
        url = self.url_favorite.format(recipe.id)
        response = client.post(url)
        code_expected = 401
        assert response.status_code == code_expected, (
            f'Убедитесь, что при обращении неавторизированного пользователя '
            f'на эндпоинт добавления рецепта в избранное `{url}`, '
            f'он получает ответ {code_expected}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_add_recipe_to_favorite(self, recipe, user_client):
        url = self.url_favorite.format(recipe.id)
        response = user_client.post(url)
        code_expected = 201
        assert response.status_code == code_expected, (
            f'Убедитесь, что при обращении авторизированного пользователя '
            f'на эндпоинт добавления рецепта в избранное `{url}`, '
            f'он получает ответ {code_expected}'
        )
        expected_fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        response_data = response.json()
        for field in expected_fields:
            assert field in response_data, (
                f'Проверьте, что при POST запросе на `{url}`, '
                f'объект списка содержит {field}'
            )

        response = user_client.post(url)
        code_expected = 400
        assert response.status_code == code_expected, (
            f'Убедитесь, что при обращении авторизированного пользователя '
            f'на эндпоинт добавления рецепта в избранное `{url}`, '
            f'если рецепт уже находится в избранном, '
            f'он получает ответ {code_expected}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_delete_recipe_from_favorite(self, recipe, user, user_client):
        FavoriteRecipe.objects.create(
            user=user,
            recipe=recipe
        )
        url = self.url_favorite.format(recipe.id)
        response = user_client.delete(url)
        code_expected = 204
        assert response.status_code == code_expected, (
            f'Убедитесь, что при обращении авторизированного пользователя '
            f'на эндпоинт удаления рецепта из избранного `{url}`, '
            f'он получает ответ {code_expected}'
        )

        response = user_client.delete(url)
        code_expected = 400
        assert response.status_code == code_expected, (
            f'Убедитесь, что при обращении авторизированного пользователя '
            f'на эндпоинт удаления рецепта из избранного `{url}`, '
            f'если рецепта там нет, он получает ответ {code_expected}'
        )
