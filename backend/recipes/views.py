from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Recipe, ShoppingCart, Favorite
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from .serializers import (
    RecipeMinifiedSerializer,
    RecipeListSerializer,
    RecipeCreateUpdateSerializer,
)
from .pagination import PagePagination
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsAuthorOrReadOnly
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404


User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    serializer_class = RecipeListSerializer
    pagination_class = PagePagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author']
    ordering_fields = ['id', 'name', 'cooking_time']
    ordering = ['id']

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeListSerializer
        elif (self.action == 'create'
              or self.action == 'update'
              or self.action == 'partial_update'):
            return RecipeCreateUpdateSerializer
        elif self.action == 'favorite' or self.action == 'shopping_cart':
            return RecipeMinifiedSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'retrieve':
            permission_classes = [permissions.AllowAny]
        elif (self.action == 'favorite'
              or self.action == 'shopping_cart'
              or self.action == 'download_shopping_cart'):
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAuthorOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Recipe.objects.all().order_by('-id')
        user = self.request.user

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart == '1' and user.is_authenticated:
            queryset = queryset.annotate(
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=user, recipe=OuterRef('pk'))
                )
            ).filter(is_in_shopping_cart=True)

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited == '1' and user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=user, recipe=OuterRef('pk'))
                )
            ).filter(is_favorited=True)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        serializer = RecipeListSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer = RecipeListSerializer(
            instance, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(self.queryset, pk=pk)
        base_url = request.get_host()
        protocol = 'https' if request.is_secure() else 'http'
        short_link = f"{protocol}://{base_url}/s/{recipe.pk}"
        print(f'short_link {short_link}')
        return Response(data={'short-link': short_link}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response({'detail': 'Рецепт уже в списке покупок'},
                                status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = self.get_serializer(
                recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            try:
                shopping_cart = ShoppingCart.objects.get(
                    user=user, recipe=recipe)
                shopping_cart.delete()
                return Response({'detail': 'Рецепт успешно удален из списка покупок'},
                                status=status.HTTP_204_NO_CONTENT)
            except ShoppingCart.DoesNotExist:
                return Response({'detail': 'Рецепт уже в списке покупок'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response({'detail': 'Рецепт уже в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = self.get_serializer(
                recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            try:
                favorite = Favorite.objects.get(user=user, recipe=recipe)
                favorite.delete()
                return Response({'detail': 'Рецепт успешно удален из избранного'},
                                status=status.HTTP_204_NO_CONTENT)
            except Favorite.DoesNotExist:
                return Response({'detail': 'Рецепта не было в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        if not shopping_cart.exists():
            return Response({'detail': 'Список покупок пуст'},
                            status=status.HTTP_404_NOT_FOUND)
        ingredients = {}
        for item in shopping_cart:
            recipe = item.recipe
            for ingredient_in_recipe in recipe.ingredients_in_recipe.all():
                ingredient = ingredient_in_recipe.ingredient
                amount = ingredient_in_recipe.amount
                if ingredient in ingredients:
                    ingredients[ingredient] += amount
                else:
                    ingredients[ingredient] = amount

        content = 'Список покупок:\n\n'
        for ingredient, amount in ingredients.items():
            content += f'- {ingredient.name} — {amount} {ingredient.measurement_unit};\n'

        response = HttpResponse(
            content, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response
