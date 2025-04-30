from django.contrib.admin import SimpleListFilter


class BooleanListFilter(SimpleListFilter):
    title = 'Boolean Filter'
    parameter_name = 'boolean_filter'
    field_name = None
    lookup_choices = (
        ('yes', 'Да'),
        ('no', 'Нет'),
    )

    def lookups(self, request, model_admin):
        return self.lookup_choices

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(**{f'{self.field_name}__isnull': False}).distinct()
        if self.value() == 'no':
            return queryset.filter(**{f'{self.field_name}__isnull': True})
        return queryset


class HasSubscriptionsFilter(BooleanListFilter):
    title = 'Есть подписки'
    parameter_name = 'has_subscriptions'
    field_name = 'subscriptions'


class HasFollowersFilter(BooleanListFilter):
    title = 'Есть подписчики'
    parameter_name = 'has_followers'
    field_name = 'subscribed_to'
