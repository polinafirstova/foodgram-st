from django.shortcuts import redirect
from django.http import Http404
from .models import Recipe


def redirect_to_recipe(request, recipe_id):
    if not Recipe.objects.filter(pk=recipe_id).exists():
        raise Http404('Рецепт не найден')
    return redirect(f'/recipes/{recipe_id}')
