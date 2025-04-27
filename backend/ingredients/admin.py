from django.contrib import admin
from .models import Ingredient, IngredientInRecipe


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientInRecipe)
