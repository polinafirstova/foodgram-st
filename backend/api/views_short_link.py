from django.shortcuts import redirect, get_object_or_404
from .models import Recipe


def redirect_to_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    recipe_url = f'/recipes/{recipe.id}'
    return redirect(recipe_url)
