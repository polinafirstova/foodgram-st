from rest_framework import viewsets, permissions, status
from .models import Ingredient, Recipe, ShoppingCart, Favorite, Subscription
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.http import FileResponse
from .serializers import (
    IngredientSerializer,
    BaseRecipeSerializer,
    RecipeListSerializer,
    RecipeCreateUpdateSerializer,
    UserSerializer,
    UserWithRecipes,
    AvatarSerializer,
)
from .pagination import PagePagination
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsAuthorOrReadOnly
from django.db.models import Exists, OuterRef, Count
from django.shortcuts import get_object_or_404
from django.urls import reverse
from datetime import datetime
from djoser.views import UserViewSet as DjoserUserViewSet


User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        name = self.request.GET.get('name')
        if name:
            return self.queryset.filter(name__startswith=name)
        return self.queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    serializer_class = RecipeListSerializer
    pagination_class = PagePagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author']
    ordering_fields = ['id', 'name', 'cooking_time']
    ordering = ['id']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        elif self.action in ['favorite', 'shopping_cart']:
            return BaseRecipeSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthorOrReadOnly]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
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
                        user=user, recipe=OuterRef('pk')
                    )
                )
            ).filter(is_in_shopping_cart=True)

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited == '1' and user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=user, recipe=OuterRef('pk')
                    )
                )
            ).filter(is_favorited=True)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(self.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance,
                                         data=request.data,
                                         partial=kwargs.pop('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(self.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        list_serializer = RecipeListSerializer(
            serializer.instance, context=self.get_serializer_context())
        self.data = list_serializer.data

    def perform_update(self, serializer):
        serializer.save()
        list_serializer = RecipeListSerializer(
            serializer.instance, context=self.get_serializer_context())
        self.data = list_serializer.data

    @action(detail=True,
            methods=['get'],
            url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(self.queryset, pk=pk)
        short_link = request.build_absolute_uri(
            reverse('redirect_to_recipe', args=[recipe.pk]))
        return Response(data={'short-link': short_link},
                        status=status.HTTP_200_OK)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self._handle_cart_or_favorite(request,
                                             pk,
                                             ShoppingCart,
                                             'Список покупок')

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        return self._handle_cart_or_favorite(request,
                                             pk,
                                             Favorite,
                                             'Избранное')

    def _handle_cart_or_favorite(self, request, pk, model, model_name):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            _, created = model.objects.get_or_create(
                user=user, recipe=recipe)
            if not created:
                return Response(
                    {'detail': f'Рецепт «{recipe.name}» уже в {model_name.lower()}'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(
                recipe, context={'request': request})
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        else:
            get_object_or_404(model, user=user, recipe=recipe).delete()
            return Response(
                {'detail': f'Рецепт успешно удален из {model_name.lower()}'},
                status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        if not shopping_cart.exists():
            return Response({'detail': 'Список покупок пуст'},
                            status=status.HTTP_404_NOT_FOUND)

        ingredients = {}
        recipes = []
        for item in shopping_cart:
            recipe = item.recipe
            recipes.append(
                f'{recipe.name} — {recipe.author.last_name} '
                + f'{recipe.author.first_name} ({recipe.author.username})')
            for ingredient_in_recipe in recipe.ingredients_in_recipe.all():
                ingredient = ingredient_in_recipe.ingredient
                amount = ingredient_in_recipe.amount
                if ingredient in ingredients:
                    ingredients[ingredient] += amount
                else:
                    ingredients[ingredient] = amount

        content = '\n'.join([
            'Список покупок\n',
            f'Дата составления: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n',
            'Продукты:',
            *[f'{i + 1}. {ingredient.name.capitalize()} — '
              + f'{amount} {ingredient.measurement_unit};' for i,
              (ingredient, amount) in enumerate(sorted(ingredients.items(),
                                                       key=lambda x: x[0].name))],
            '\nРецепты:',
            *[f'{i + 1}. {recipe};' for i, recipe in enumerate(recipes)],
        ])

        return FileResponse(content,
                            content_type='text/plain; charset=utf-8')


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all().order_by('id')
    queryset = queryset.annotate(
        recipes_count=Count('recipes')
    )
    serializer_class = UserSerializer
    pagination_class = PagePagination
    permission_classes = [permissions.AllowAny]

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        return super().me(request, pk=request.user.pk)

    @action(detail=True,
            methods=['post', 'delete'],
            serializer_class=UserWithRecipes,
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        author = self.get_object()
        user = request.user

        if request.method == 'POST':
            if user == author:
                return Response({'detail': 'Нельзя подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            _, created = Subscription.objects.get_or_create(
                user=user, author=author)
            if not created:
                return Response({'detail': 'Подписка уже оформлена'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(self.get_serializer(author).data,
                            status=status.HTTP_201_CREATED)
        else:
            get_object_or_404(Subscription,
                              user=user,
                              author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            serializer_class=UserWithRecipes,
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        subscriptions = Subscription.objects.filter(
            user=user).values_list('author', flat=True)
        queryset = User.objects.filter(id__in=subscriptions).annotate(
            recipes_count=Count('recipes')
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data)

        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False,
            url_path='me/avatar',
            methods=['put', 'delete'],
            serializer_class=AvatarSerializer,
            permission_classes=[permissions.IsAuthenticated])
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                request.user.avatar = serializer.validated_data['avatar']
                request.user.save()
                avatar_url = request.user.avatar.url if request.user.avatar else None
                return Response({'avatar': avatar_url}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            if request.user.avatar:
                request.user.avatar.delete()
            request.user.avatar = None
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
