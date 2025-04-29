from django.contrib import admin
from .models import Ingredient, IngredientInRecipe, Recipe, Favorite, ShoppingCart
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.contrib.admin import SimpleListFilter


User = get_user_model()


class HasRecipesFilter(SimpleListFilter):
    title = 'Используется в рецептах'
    parameter_name = 'has_recipes'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(ingredientinrecipe__isnull=False).distinct()
        if self.value() == 'no':
            return queryset.filter(ingredientinrecipe__isnull=True)
        return queryset


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

    @admin.display(description='Number of Recipes')
    def recipe_count(self, ingredient):
        return ingredient.ingredients_in_recipe.count()

    @admin.display(boolean=True, description='Used in Recipes')
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


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time_range'

    def calculate_thresholds(self, queryset):
        all_times = [recipe.cooking_time for recipe in queryset]
        if len(all_times) < 3:
            return 30, 60
        all_times.sort()
        n = all_times[len(all_times) // 3]
        m = all_times[2 * len(all_times) // 3]
        return n, m

    def lookups(self, request, model_admin):
        queryset = model_admin.model.objects.all()
        n, m = self.calculate_thresholds(queryset)

        less_than_n_count = queryset.filter(cooking_time__lt=n).count()
        between_n_m_count = queryset.filter(
            cooking_time__gte=n, cooking_time__lt=m).count()
        greater_than_m_count = queryset.filter(cooking_time__gte=m).count()

        return (
            ('fast', f'Быстрее {n} мин ({less_than_n_count})'),
            ('medium', f'От {n} до {m} мин ({between_n_m_count})'),
            ('long', f'Более {m} мин ({greater_than_m_count})'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        n, m = self.calculate_thresholds(queryset)

        if value == 'fast':
            return queryset.filter(cooking_time__lt=n)
        elif value == 'medium':
            return queryset.filter(cooking_time__gte=n, cooking_time__lt=m)
        elif value == 'long':
            return queryset.filter(cooking_time__gte=m)
        return queryset


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

    @admin.display(description='Ингредиенты')
    def ingredients_list(self, recipe):
        ingredients = IngredientInRecipe.objects.filter(recipe=recipe)
        return format_html('<br>'.join([str(ingredient) for ingredient in ingredients]))

    @admin.display(description='Картинка')
    @mark_safe
    def recipe_image(self, recipe):
        if recipe.image:
            return f'<img src="{recipe.url}" width="50" height="50" />'
        return ""


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'recipe')


class HasSubscriptionsFilter(SimpleListFilter):
    title = 'Есть подписки'
    parameter_name = 'has_subscriptions'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(subscriptions__isnull=False).distinct()
        if self.value() == 'no':
            return queryset.filter(subscriptions__isnull=True)
        return queryset


class HasFollowersFilter(SimpleListFilter):
    title = 'Есть подписчики'
    parameter_name = 'has_followers'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(subscribed_to__isnull=False).distinct()
        if self.value() == 'no':
            return queryset.filter(subscribed_to__isnull=True)
        return queryset


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
    list_filter = (HasRecipesFilter,
                   HasSubscriptionsFilter,
                   HasFollowersFilter)

    def full_name(self, user):
        return f"{user.first_name} {user.last_name}"
    full_name.short_description = 'ФИО'

    @admin.display(description='Аватар')
    @mark_safe
    def avatar(self, user):
        if user.avatar:
            return f'<img src="{user.avatar.url}" width="50" height="50" />'
        return "Нет аватара"

    def recipe_count(self, user):
        return user.recipes.count()
    recipe_count.short_description = 'Количество рецептов'

    def subscription_count(self, user):
        return user.subscriptions.count()
    subscription_count.short_description = 'Количество подписок'

    def follower_count(self, user):
        return user.authors.count()
    follower_count.short_description = 'Количество подписчиков'

    def has_recipes(self, user):
        return user.recipes.exists()
    has_recipes.boolean = True
    has_recipes.short_description = 'Есть рецепты'

    def has_subscriptions(self, user):
        return user.subscriptions.exists()
    has_subscriptions.boolean = True
    has_subscriptions.short_description = 'Есть подписки'

    def has_followers(self, user):
        return user.authors.exists()
    has_followers.boolean = True
    has_followers.short_description = 'Есть подписчики'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            recipe_count=Count('recipes', distinct=True),
            subscription_count=Count('subscriptions', distinct=True),
            follower_count=Count('authors', distinct=True)
        )
        return queryset
