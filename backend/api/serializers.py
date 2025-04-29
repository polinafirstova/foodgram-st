from rest_framework import serializers
from .models import Ingredient, IngredientInRecipe, Recipe, Subscription
from django.contrib.auth import get_user_model
from .fields import Base64ToImageField, Base64RequiredImageField
from rest_framework.exceptions import ValidationError
from djoser.serializers import UserSerializer as DjoserUserSerializer


User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id',
                  'name',
                  'measurement_unit')


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        read_only=True, source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = ('id',
                  'name',
                  'measurement_unit',
                  'amount')


class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        required=True
    )
    amount = serializers.IntegerField(min_value=1, required=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id',
                  'amount')


class BaseRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time')
        read_only_fields = ('id',)


class RecipeAuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'avatar')

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user,
                                               author=author).exists()
        return False


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    image = Base64RequiredImageField(required=True)
    ingredients = IngredientInRecipeWriteSerializer(many=True, required=True)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = ('id',
                  'ingredients',
                  'name',
                  'image',
                  'text',
                  'cooking_time')

    def validate_ingredients(self, ingredients_data):
        print(f'ingredients_data {ingredients_data}')
        if not ingredients_data:
            raise ValidationError(
                {'ingredients': 'Необходимо указать хотя бы один ингредиент'})

        ingredients_ids = set()
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['id'].pk
            if ingredient_id in ingredients_ids:
                raise ValidationError(
                    {'ingredients': f'Ингредиент с ID {ingredient_id} дублируется'})
            ingredients_ids.add(ingredient_id)
        return ingredients_data

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients_data = validated_data.pop('ingredients')
        validated_data['author'] = request.user
        recipe = super().create(validated_data)
        recipe.save()
        self._create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        self.validate_ingredients(ingredients_data)
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self._create_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def _create_ingredients(self, recipe, ingredients_data):
        ingredients_to_create = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount'])
            for ingredient_data in ingredients_data
        ]
        IngredientInRecipe.objects.bulk_create(ingredients_to_create)


class RecipeListSerializer(BaseRecipeSerializer):
    author = RecipeAuthorSerializer(read_only=True)
    ingredients = IngredientInRecipeReadSerializer(
        many=True, read_only=True, source='ingredients_in_recipe')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta(BaseRecipeSerializer.Meta):
        fields = BaseRecipeSerializer.Meta.fields + (
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'text')

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return recipe.favorites.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return recipe.shopping_cart.filter(user=request.user).exists()
        return False


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.ImageField(read_only=True)

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = DjoserUserSerializer.Meta.fields + (
            'is_subscribed',
            'avatar')

    def get_is_subscribed(self, user):
        request_user = self.context['request'].user
        if request_user.is_anonymous:
            return False
        return Subscription.objects.filter(user=request_user, author=user).exists()


class UserWithRecipes(UserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.ReadOnlyField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count')

    def get_recipes(self, user):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            limit = None

        recipes = user.recipes.all()
        if limit:
            recipes = recipes[:limit]

        return BaseRecipeSerializer(recipes,
                                    many=True,
                                    context={'request': request}).data


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ToImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)
