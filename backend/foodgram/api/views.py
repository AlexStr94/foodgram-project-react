from io import StringIO

from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser import utils
from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.views import UserViewSet
from rest_framework import filters, pagination, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from recipes.models import (FavoriteRecipe, Ingredient, Recipe, RecipeInCart,
                            Tag)
from users.models import Subscription, User

from .filters import RecipeFilter
from .permissions import RecipePermission
from .serializers import (FavoriteRecipeSerializer, GetTokenSerializer,
                          IngredientSerializer, RecipeInCartSerializer,
                          RecipeSerializer, TagSerializer,
                          UserInSubscriptionSerializer)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    if serializer.is_valid():
        data = {'auth_token': serializer.data.get('token')}
        return Response(data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(UserViewSet):
    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserInSubscriptionSerializer
    )
    def subscribe(self, request, *args, **kwargs):
        follower = request.user
        user = self.get_object()
        subscription_existing = Subscription.objects.filter(
            user=user,
            follower=follower
        ).exists()
        if request.method == 'POST':
            if subscription_existing:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            subscription = Subscription.objects.create(
                user=user,
                follower=follower
            )
            serializer = self.get_serializer(instance=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not subscription_existing:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        subscription = Subscription.objects.get(
            user=user,
            follower=follower
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserInSubscriptionSerializer
    )
    def subscriptions(self, request, *args, **kwargs):
        user = request.user
        users = User.objects.filter(followers__follower=user)
        paginator = pagination.PageNumberPagination()
        paginated_products = paginator.paginate_queryset(users, request)
        serializer = self.get_serializer(
            paginated_products,
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": self.request.user}
            to = [get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(
                self.request,
                context
            ).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response(
            data=serializer.data,
            status=status.HTTP_204_NO_CONTENT
        )


class TagReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class IngredientReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (RecipePermission,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = self.get_object()
        recipe_in_cart_existing = RecipeInCart.objects.filter(
            user=user,
            recipe=recipe
        ).exists()
        if request.method == 'POST':
            if recipe_in_cart_existing:
                return Response(
                    {'errors': 'Рецепт уже добавлен в корзину'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe = RecipeInCart.objects.create(user=user, recipe=recipe)
            serializer = RecipeInCartSerializer(
                instance=recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not recipe_in_cart_existing:
            return Response(
                {'errors': 'Нельзя удалить то, чего нет'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = RecipeInCart.objects.get(user=user, recipe=recipe)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = self.get_object()
        recipe_in_favorite = FavoriteRecipe.objects.filter(
            user=user,
            recipe=recipe
        ).exists()
        if request.method == 'POST':
            if recipe_in_favorite:
                return Response(
                    {'errors': 'Рецепт уже добавлен в избранное'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe = FavoriteRecipe.objects.create(user=user, recipe=recipe)
            serializer = FavoriteRecipeSerializer(
                instance=recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not recipe_in_favorite:
            return Response(
                {'errors': 'Нельзя удалить то, чего нет'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = FavoriteRecipe.objects.get(user=user, recipe=recipe)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        user = request.user
        shopping_cart = {}
        for obj in RecipeInCart.objects.filter(user=user):
            ingredients = obj.recipe.ingredients.all()
            for ingredient in ingredients:
                if shopping_cart.get(ingredient.name):
                    shopping_cart[ingredient.name] += ingredient.amount
                else:
                    shopping_cart[ingredient.name] = ingredient.amount
        shopping_cart = [
            '{}: {}\n'.format(key, val) for key, val in shopping_cart.items()
        ]
        file = StringIO(
            'Список покупок:\n ',
            ''.join(shopping_cart)
        )
        return HttpResponse(file, content_type='text/plain')
