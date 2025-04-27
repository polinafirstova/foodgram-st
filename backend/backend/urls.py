from django.contrib import admin
from django.urls import path, include
from recipes.views_short_link import redirect_to_recipe

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('recipes.urls')),
    path('api/', include('ingredients.urls')),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('s/<int:recipe_id>/', redirect_to_recipe,
         name="redirect_short_link"),
]
