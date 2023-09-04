from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, IngredientViewSet, TagViewSet, RecipeViewSet

router_v1 = DefaultRouter()
router_v1.register(r'users', CustomUserViewSet, basename='users')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('recipes/download_shopping_cart/',
         RecipeViewSet.as_view(
             {
                 'get': 'download_shopping_cart',
             }
         ), name='recipe-download-shopping-cart'),
    path('recipes/<int:pk>/favorite/',
         RecipeViewSet.as_view(
             {
                 'post': 'add_to_favorites',
                 'delete': 'remove_from_favorites'
             }
         ), name='recipe-favorite'),
    path('recipes/<int:pk>/shopping_cart/',
         RecipeViewSet.as_view(
             {
                 'post': 'add_to_shopping_cart',
                 'delete': 'remove_from_shopping_cart'
             }
         ), name='recipe-shopping-cart'),

    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
