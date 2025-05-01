from django.contrib import admin
from .models import Ingredient, IngredientInRecipe, Recipe, Favorite, ShoppingCart
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from .filters import CookingTimeFilter, HasSubscriptionsFilter, HasFollowersFilter
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count


User = get_user_model()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'measurement_unit',
                    'recipe_count')
    search_fields = ('name',
                     'measurement_unit')
    list_filter = ('measurement_unit',)

    @admin.display(description='Рецептов')
    def recipe_count(self, ingredient):
        return ingredient.ingredients_in_recipe.count()


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
            return f'<img src="{recipe.image.url}" width="50" height="50" />'
        return ""


@admin.register(Favorite, ShoppingCart)
class FavoriteOrShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'recipe')


@admin.register(User)
class UserAdminExtended(UserAdmin):
    list_display = ('id',
                    'username',
                    'full_name',
                    'email',
                    'avatar', ''
                    'recipe_count',
                    'subscription_count',
                    'follower_count')
    search_fields = ('username',
                     'email',
                     'first_name',
                     'last_name')
    list_filter = (HasSubscriptionsFilter,
                   HasFollowersFilter)

    @admin.display(description='ФИО')
    def full_name(self, user):
        return f"{user.first_name} {user.last_name}"

    @admin.display(description='Аватар')
    @mark_safe
    def avatar(self, user):
        if user.avatar:
            return f'<img src="{user.avatar.url}" width="50" height="50" />'
        return "Нет аватара"

    @admin.display(description='Рецептов')
    def recipe_count(self, user):
        return user.recipe_count

    @admin.display(description='Подписок')
    def subscription_count(self, user):
        return user.subscription_count

    @admin.display(description='Подписчиков')
    def follower_count(self, user):
        return user.follower_count

    @admin.display(description='Есть подписки', boolean=True)
    def has_subscriptions(self, user):
        return user.subscriptions.exists()

    @admin.display(description='Есть подписчики', boolean=True)
    def has_followers(self, user):
        return user.authors.exists()

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            recipe_count=Count('recipes', distinct=True),
            subscription_count=Count('subscriptions', distinct=True),
            follower_count=Count('authors', distinct=True)
        )
        return queryset
