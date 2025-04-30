from django.contrib.admin import SimpleListFilter
from api.filters import BooleanListFilter


class HasRecipesFilter(BooleanListFilter):
    title = 'Используется в рецептах'
    parameter_name = 'has_recipes'
    field_name = 'ingredients_in_recipe'


class CookingTimeFilter(SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time_range'
    thresholds = None

    def calculate_thresholds(self, queryset):
        all_times = sorted(queryset.values_list(
            'cooking_time', flat=True).distinct())
        if len(all_times) < 3:
            if len(all_times) == 0:
                return None, None
            elif len(all_times) == 1:
                return all_times[0] - 10, all_times[0] + 10
            else:
                return (all_times[0] + (all_times[1] - all_times[0]) // 3,
                        all_times[1] - (all_times[1] - all_times[0]) // 3)

        n = all_times[len(all_times) // 3]
        m = all_times[2 * len(all_times) // 3]
        return n, m

    def lookups(self, request, model_admin):
        queryset = model_admin.model.objects.all()
        n, m = self.thresholds

        if n is None or m is None:
            return []

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
        n, m = self.thresholds

        if value == 'fast':
            return queryset.filter(cooking_time__lt=n)
        elif value == 'medium':
            return queryset.filter(cooking_time__gte=n, cooking_time__lt=m)
        elif value == 'long':
            return queryset.filter(cooking_time__gte=m)
        return queryset
