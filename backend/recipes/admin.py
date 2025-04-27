from django.contrib import admin
from django.utils.html import format_html
from .models import Recipe, Favorite, ShoppingCart, Tag
from ingredients.models import IngredientInRecipe


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInRecipeInline]
    list_display = ('name', 'author', 'cooking_time', 'favorites_count')
    list_filter = ('author',)
    search_fields = ('name', 'text', 'author__username',
                     'author__first_name', 'author__last_name')
    readonly_fields = ('favorites_count',)

    def favorites_count(self, obj):
        return obj.favorites.count()
    favorites_count.short_description = 'Добавлено в избранное'

    def ingredientinrecipe_set(self, obj):
        ingredients = IngredientInRecipe.objects.filter(recipe=obj)
        return format_html('<br>'.join([str(ingredient) for ingredient in ingredients]))

    ingredientinrecipe_set.short_description = 'Ингредиенты'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
admin.site.register(Tag)
