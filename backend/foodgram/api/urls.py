from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (CustomUserViewSet, IngredientReadOnlyModelViewSet,
                    RecipeViewSet, TagReadOnlyModelViewSet, get_token)

router_v1 = SimpleRouter()
router_v1.register(
    'tags', TagReadOnlyModelViewSet,
    basename='tags'
)
router_v1.register(
    'ingredients', IngredientReadOnlyModelViewSet,
    basename='ingredients'
)
router_v1.register(
    'recipes', RecipeViewSet,
    basename='recipes'
)
router_v1.register(
    'users',
    CustomUserViewSet,
    basename='users'
)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/token/login/', get_token),
    path('auth/', include('djoser.urls.authtoken')),
]
