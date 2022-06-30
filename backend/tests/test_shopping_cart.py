import pytest
from recipes.models import RecipeInCart


class TestShoppingCartApi:
    url_shopping_cart = '/api/recipes/{}/shopping_cart/'

    @pytest.mark.django_db(transaction=True)
    def test_add_recipe_to_cart_not_auth(self, recipe, client):
        url = self.url_shopping_cart.format(recipe.id)
        response = client.post(url)
        code_expected = 401
        assert response.status_code == code_expected, (
            f'Убедитесь, что при обращении неавторизированного пользователя '
            f'на эндпоинт добавления рецепта в избранное `{url}`, '
            f'он получает ответ {code_expected}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_add_recipe_to_cart(self, recipe, user_client):
        url = self.url_shopping_cart.format(recipe.id)
        response = user_client.post(url)
        code_expected = 201
        assert response.status_code == code_expected, (
            f'Убедитесь, что при обращении авторизированного пользователя '
            f'на эндпоинт добавления рецепта в корзину `{url}`, '
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
            f'на эндпоинт добавления рецепта в корзину `{url}`, '
            f'если рецепт уже находится в избранном, '
            f'он получает ответ {code_expected}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_delete_recipe_from_cart(self, recipe, user, user_client):
        RecipeInCart.objects.create(
            user=user,
            recipe=recipe
        )
        url = self.url_shopping_cart.format(recipe.id)
        response = user_client.delete(url)
        code_expected = 204
        assert response.status_code == code_expected, (
            f'Убедитесь, что при обращении авторизированного пользователя '
            f'на эндпоинт удаления рецепта из корзину `{url}`, '
            f'он получает ответ {code_expected}'
        )

        response = user_client.delete(url)
        code_expected = 400
        assert response.status_code == code_expected, (
            f'Убедитесь, что при обращении авторизированного пользователя '
            f'на эндпоинт удаления рецепта из корзину `{url}`, '
            f'если рецепта там нет, он получает ответ {code_expected}'
        )
