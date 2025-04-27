from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import (
    BaseUserSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserWithRecipes,
    AvatarSerializer,
    SetPasswordSerializer,
)
from .pagination import PagePagination
from .models import Subscription
from .permissions import IsOwnerOrReadOnly


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = BaseUserSerializer
    pagination_class = PagePagination
    ordering_fields = ['id', 'username', 'email']
    ordering = ['id']

    def get_queryset(self):
        queryset = User.objects.all().order_by('id')
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'list' or self.action == 'retrieve' or self.action == 'me':
            return UserSerializer
        elif self.action == 'subscribe' or self.action == 'subscriptions':
            return UserWithRecipes
        elif self.action == 'avatar':
            return AvatarSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer
        return BaseUserSerializer

    def get_permissions(self):
        if (self.action == 'create'
            or self.action == 'list'
            or self.action == 'retrieve'
                or self.action == 'subscriptions'):
            permission_classes = [permissions.AllowAny]
        elif (self.action == 'me'
              or self.action == 'set_password'
              or self.action == 'avatar'
              or self.action == 'subscribe'):
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk=None):
        author = self.get_object()
        user = request.user

        if user == author:
            return Response({'detail': 'Нельзя подписаться на себя'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response({'detail': 'Подписка уже офромлена'},
                                status=status.HTTP_400_BAD_REQUEST)

            Subscription.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            try:
                subscription = Subscription.objects.get(
                    user=user, author=author)
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Subscription.DoesNotExist:
                return Response({'detail': 'Подписка не была оформлена'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        subscriptions = Subscription.objects.filter(
            user=user).values_list('author', flat=True)
        queryset = User.objects.filter(id__in=subscriptions)

        limit = request.query_params.get('limit')
        if limit:
            queryset = queryset[:int(limit)]

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'],
            serializer_class=SetPasswordSerializer,
            permission_classes=[permissions.IsAuthenticated])
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if not request.user.check_password(
                    serializer.validated_data['current_password']):
                return Response({'current_password': ['Неверный текущий пароль']},
                                status=status.HTTP_400_BAD_REQUEST)
            request.user.set_password(
                serializer.validated_data['new_password'])
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

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
            request.user.avatar = None
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
