from django.contrib.admin import SimpleListFilter


class CookingTimeFilter(SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time_range'
    thresholds = None

    def calculate_thresholds(self, queryset):
        all_times = sorted(queryset.values_list(
            'cooking_time', flat=True).distinct())
        if len(all_times) < 3:
            return None

        n = all_times[len(all_times) // 3]
        m = all_times[2 * len(all_times) // 3]
        return n, m

    def lookups(self, request, model_admin):
        if self.thresholds is None:
            queryset = model_admin.model.objects.all()
            self.thresholds = self.calculate_thresholds(queryset)

        if self.thresholds is None:
            return []

        n, m = self.thresholds

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
        if self.thresholds is None:
            return queryset

        n, m = self.thresholds

        if value == 'fast':
            return queryset.filter(cooking_time__lt=n)
        elif value == 'medium':
            return queryset.filter(cooking_time__gte=n, cooking_time__lt=m)
        elif value == 'long':
            return queryset.filter(cooking_time__gte=m)
        return queryset


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
    field_name = 'authors'
