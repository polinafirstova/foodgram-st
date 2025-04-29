from django.contrib import admin
from django.urls import path, include
from api.views_short_link import redirect_to_recipe

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<int:recipe_id>/', redirect_to_recipe,
         name="redirect_to_recipe"),
]
