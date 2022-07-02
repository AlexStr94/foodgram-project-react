from colorfield.fields import ColorField
from django.db import models
from pytils.translit import slugify

from users.models import User


class Tag(models.Model):
    """ Модель описывающая теги для рецептов."""
    name = models.CharField('Название', max_length=200)
    color = ColorField(
        format='hex',
        max_length=7,
        unique=True
    )
    slug = models.SlugField(
        'URL',
        max_length=200,
        blank=True,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег для рецептов'
        verbose_name_plural = 'Теги для рецептов'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if len(self.slug) > 200:
                self.slug = self.slug[:200]
        super(Tag, self).save(*args, **kwargs)


class Ingredient(models.Model):
    """ Модель описывающая ингредиенты для рецептов."""
    name = models.CharField(
        'Название',
        max_length=200,
        unique=True
    )
    measurement_unit = models.ForeignKey(
        'MeasurementUnit',
        on_delete=models.PROTECT,
        related_name='ingredients',
        verbose_name='Мера измерения'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class MeasurementUnit(models.Model):
    """ Модель описывающая меры измерения"""
    name = models.CharField(
        'Название',
        unique=True,
        max_length=200
    )

    class Meta:
        verbose_name = 'Мера измерения'
        verbose_name_plural = 'Меры измерения'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """ Модель описывающая ингредиент в составе рецепта."""
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='recipe_ingredient',
        verbose_name='Ингредиент'
    )
    amount = models.IntegerField('Кол-во')

    class Meta:
        verbose_name = 'Ингредиент из рецепта'
        verbose_name_plural = 'Ингредиенты из рецептов'

    def __str__(self):
        return f'Ингредиент "{self.ingredient}" в рецепте "{self.recipe}"'

    @property
    def name(self):
        return self.ingredient.name

    @property
    def measurement_unit(self):
        return self.ingredient.measurement_unit.name


class Recipe(models.Model):
    """ Модель описывающая рецепты."""
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='recipes',
        verbose_name='Автор',
        null=True
    )
    name = models.CharField(
        'Название',
        max_length=200,
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/'
    )
    text = models.TextField(
        'Описание'
    )
    cooking_time = models.IntegerField(
        'Время приготовления',
        help_text='Необходимо указывать в минутах'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'Рецепт "{self.name}"'

    def count_in_favorite(self):
        return FavoriteRecipe.objects.filter(recipe=self).count()

    count_in_favorite.short_description = 'Добавлено в избранное (раз)'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Рецепт из избранного'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='one_recipe_favorite'
            ),
        )

    def __str__(self):
        return f'{self.recipe} в избранном у пользователя {self.user}'


class RecipeInCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes_in_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='one_recipe_favorite'
            ),
        )

    def __str__(self):
        return f'{self.recipe} в корзине у пользователя {self.user}'
