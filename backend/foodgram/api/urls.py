from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (CustomUserViewSet, IngredientReadOnlyModelViewSet,
                    RecipeViewSet, TagReadOnlyModelViewSet, get_token)

router_v1 = SimpleRouter()
router_v1.register(
    r'tags', TagReadOnlyModelViewSet
)
router_v1.register(
    r'ingredients', IngredientReadOnlyModelViewSet
)
router_v1.register(
    r'recipes', RecipeViewSet
)
router_v1.register(
    r'users',
    CustomUserViewSet
)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/token/login/', get_token),
    path('auth/', include('djoser.urls.authtoken')),
]
