from django.db import transaction
from djoser.conf import settings
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import exceptions, serializers
from rest_framework.authtoken.models import Token

from recipes.models import (FavoriteRecipe, Ingredient, IngredientInRecipe,
                            MeasurementUnit, Recipe, RecipeInCart, Tag)
from users.models import Subscription, User


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
            'password',
            'email',
            'first_name',
            'last_name'
        )


class GetTokenSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254)
    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        email = list(obj.items())[0][1]
        user = User.objects.get(
            email=email
        )
        token, created = Token.objects.get_or_create(user=user)
        return token.key

    def validate(self, data):
        email = data['email']
        password = data['password']
        try:
            user = User.objects.get(email=email)
        except Exception:
            raise exceptions.AuthenticationFailed('Данные не верные')
        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Данные не верные')
        return data

    class Meta:
        model = User
        fields = ('email', 'password', 'token')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class TagField(serializers.RelatedField):

    def get_queryset(self):
        return Tag.objects.all()

    def to_internal_value(self, data):
        id = data
        try:
            tag = Tag.objects.get(id=id)
        except Exception:
            raise serializers.ValidationError('Тега с таким id не существует')
        return tag

    def to_representation(self, value):
        return TagSerializer(value).data


class BaseUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        follower = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            follower = request.user
        else:
            return False
        existing = Subscription.objects.filter(
            follower=follower.id,
            user=obj
        ).exists()
        return existing


class RecipeInSubscriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserInSubscriptionSerializer(BaseUserSerializer):
    recipes = RecipeInSubscriptionsSerializer(many=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.SlugRelatedField(
        slug_field='name',
        queryset=MeasurementUnit.objects.all()
    )

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeGetSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_id(self, obj):
        return obj.ingredient.id


class IngredientInRecipeField(serializers.RelatedField):
    default_error_messages = {
        'required id': ('Поле id является обязательным'),
        'required amount': ('Поле amount является обязательным'),
        'min_amount_error': ('Значение поля amount должно быть больше 0')
    }

    def get_queryset(self):
        return IngredientInRecipe.objects.all()

    def to_representation(self, value):
        return IngredientInRecipeGetSerializer(value).data

    def to_internal_value(self, data):
        if data.get('id') is None:
            self.fail('required id')
        if data.get('amount') is None:
            self.fail('required amount')
        if int(data.get('amount')) < 1:
            self.fail('min_amount_error')
        return data


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeField(many=True)
    image = Base64ImageField()
    tags = TagField(many=True)
    author = BaseUserSerializer(default=serializers.CurrentUserDefault())
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        existing = FavoriteRecipe.objects.filter(
            user=user.id,
            recipe=obj
        ).exists()
        return existing

    def get_is_in_shopping_cart(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        existing = RecipeInCart.objects.filter(
            user=user.id,
            recipe=obj
        ).exists()
        return existing

    def _create_ingr_in_recipe(self, recipe, ingredients):
        for ingredient_data in ingredients:
            ingredient_id = ingredient_data['id']
            ingredient = Ingredient.objects.get(id=ingredient_id)
            amount = ingredient_data['amount']
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

    def create(self, validated_data):
        with transaction.atomic():
            ingredients = validated_data.pop('ingredients', None)
            tags = validated_data.pop('tags', None)
            recipe = Recipe(**validated_data)
            recipe.save()
            field = getattr(recipe, 'tags')
            field.set(tags)
            self._create_ingr_in_recipe(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        with transaction.atomic():
            ingredients = validated_data.pop('ingredients', None)
            tags = validated_data.pop('tags', None)

            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            instance.save()

            tags_field = getattr(instance, 'tags')
            tags_field.set(tags)

            IngredientInRecipe.objects.filter(recipe=instance).delete()

            self._create_ingr_in_recipe(instance, ingredients)

        return instance


class RecipeInCartSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    cooking_time = serializers.SerializerMethodField()

    class Meta:
        model = RecipeInCart
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_id(self, obj):
        return obj.recipe.id

    def get_name(self, obj):
        return obj.recipe.name

    def get_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.recipe.image)

    def get_cooking_time(self, obj):
        return obj.recipe.cooking_time


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    cooking_time = serializers.SerializerMethodField()

    class Meta:
        model = FavoriteRecipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_id(self, obj):
        return obj.recipe.id

    def get_name(self, obj):
        return obj.recipe.name

    def get_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.recipe.image)

    def get_cooking_time(self, obj):
        return obj.recipe.cooking_time
