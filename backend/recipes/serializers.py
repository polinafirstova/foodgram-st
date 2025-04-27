from rest_framework import serializers
from .models import Recipe
from ingredients.serializers import IngredientInRecipeSerializer
from ingredients.models import Ingredient, IngredientInRecipe
from django.contrib.auth import get_user_model
from .fields import CustomBase64ImageField
from users.models import Subscription
from rest_framework.exceptions import ValidationError


User = get_user_model()


class BaseRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time')
        read_only_fields = ('id',)


class RecipeMinifiedSerializer(BaseRecipeSerializer):
    class Meta(BaseRecipeSerializer.Meta):
        fields = BaseRecipeSerializer.Meta.fields


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

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, author=obj).exists()
        return False


class IngredientInRecipeCreateSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    image = CustomBase64ImageField(required=True)
    ingredients = IngredientInRecipeCreateSerializer(
        many=True, write_only=True)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = ('name',
                  'image',
                  'text',
                  'cooking_time',
                  'ingredients')

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients_data = validated_data.pop('ingredients')
        author = request.user

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

        recipe = Recipe.objects.create(author=author, **validated_data)

        for ingredient_data in ingredients_data:
            IngredientInRecipe.objects.create(
                recipe=recipe, ingredient=ingredient_data['id'], amount=ingredient_data['amount'])

        return recipe

    def update(self, instance, validated_data):
        request = self.context.get('request')
        ingredients_data = validated_data.pop('ingredients', None)

        if not ingredients_data:
            raise ValidationError(
                {'ingredients': 'Необходимо указать хотя бы один ингредиент'})

        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.save()

        if ingredients_data is not None:
            IngredientInRecipe.objects.filter(recipe=instance).delete()
            ingredients_ids = set()
            for ingredient_data in ingredients_data:
                ingredient_id = ingredient_data['id'].pk
                if ingredient_id in ingredients_ids:
                    raise ValidationError(
                        {'ingredients': f'Ингредиент с ID {ingredient_id} дублируется'})
                ingredients_ids.add(ingredient_id)
                IngredientInRecipe.objects.create(
                    recipe=instance, ingredient=ingredient_data['id'], amount=ingredient_data['amount'])

        return instance


class RecipeListSerializer(BaseRecipeSerializer):
    author = RecipeAuthorSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
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

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.shopping_cart.filter(user=request.user).exists()
        return False
