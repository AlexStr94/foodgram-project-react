from django_filters.rest_framework import BooleanFilter, CharFilter, FilterSet

from recipes.models import Ingredient, Recipe


class RecipeFilter(FilterSet):
    tags = CharFilter(field_name='tags__slug')
    is_favorited = BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs['request'].user
        super(RecipeFilter, self).__init__(*args, **kwargs)

    def filter_is_favorited(self, qs, name, value):
        if value:
            qs = qs.filter(favorites__user=self.user)
        return qs

    def filter_is_in_shopping_cart(self, qs, name, value):
        if value:
            qs = qs.filter(cart__user=self.user)
        return qs


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)
