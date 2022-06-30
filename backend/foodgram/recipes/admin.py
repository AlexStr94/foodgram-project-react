from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, IngredientInRecipe,
                     MeasurementUnit, Recipe, RecipeInCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(MeasurementUnit)
class MeasurementUnitAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author',)
    list_filter = ('author', 'tags')
    readonly_fields = ('count_in_favorite',)
    search_fields = ('author__username', 'name',)


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(RecipeInCart)
class RecipeInCartAdmin(admin.ModelAdmin):
    pass
