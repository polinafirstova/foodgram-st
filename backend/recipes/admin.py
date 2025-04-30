from django.contrib import admin
from .models import Ingredient, IngredientInRecipe, Recipe, Favorite, ShoppingCart
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from .filters import HasRecipesFilter, CookingTimeFilter


User = get_user_model()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'measurement_unit',
                    'recipe_count',
                    'has_recipes')
    search_fields = ('name',
                     'measurement_unit')
    list_filter = ('measurement_unit',
                   HasRecipesFilter)

    @admin.display(description='Количество рецептов')
    def recipe_count(self, ingredient):
        return ingredient.ingredients_in_recipe.count()

    @admin.display(boolean=True, description='Используется в рецептах')
    def has_recipes(self, ingredient):
        return ingredient.ingredients_in_recipe.exists()


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe',
                    'ingredient',
                    'amount')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInRecipeInline]
    list_display = ('id',
                    'name',
                    'cooking_time',
                    'author',
                    'favorites_count',
                    'ingredients_list',
                    'recipe_image')
    list_filter = ('author',
                   CookingTimeFilter)
    search_fields = ('name',
                     'text',
                     'author__username',
                     'author__first_name',
                     'author__last_name')
    readonly_fields = ('favorites_count',)

    @admin.display(description='Добавлено в избранное')
    def favorites_count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Продукты')
    @mark_safe
    def ingredients_list(self, recipe):
        ingredients = recipe.ingredients_in_recipe.all()
        return ('<br>'.join(str(ingredient) for ingredient in ingredients))

    @admin.display(description='Картинка')
    @mark_safe
    def recipe_image(self, recipe):
        if recipe.image:
            return f'<img src="{recipe.url}" width="50" height="50" />'
        return ""


@admin.register(Favorite, ShoppingCart)
class FavoriteOrShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'recipe')
