from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.db.models import Count
from recipes.admin import HasRecipesFilter
from .filters import HasSubscriptionsFilter, HasFollowersFilter


User = get_user_model()


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

    @admin.display(description='ФИО')
    def full_name(self, user):
        return f"{user.first_name} {user.last_name}"

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
