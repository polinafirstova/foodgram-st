from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(
        verbose_name=_('Адрес электронной почты'),
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name=_('Имя'),
        max_length=150,
        blank=False,
    )
    last_name = models.CharField(
        verbose_name=_('Фамилия'),
        max_length=150,
        blank=False,
    )
    username = models.CharField(
        verbose_name=_('Имя пользователя'),
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text=(
            _("Обязательное. 150 символов или менее. Буквы, цифры и @/./+/-/_ только.")
        ),
        validators=[AbstractUser.username_validator],
        error_messages={
            "unique": _("Пользователь с таким именем уже существует."),
        },
    )
    avatar = models.ImageField(
        verbose_name=_('Аватар'),
        help_text=_('Аватар'),
        upload_to='users/images/',
        null=True,
        blank=True
    )
    is_subscribed = models.BooleanField(
        verbose_name=_('Подписан'),
        default=False,
        help_text=_('Подписан ли текущий пользователь на этого')
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return self.email


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=_('Подписчик')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_to',
        verbose_name=_('Автор')
    )

    class Meta:
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
