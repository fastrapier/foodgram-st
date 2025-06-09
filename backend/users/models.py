from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя с email как основным полем для входа."""

    email = models.EmailField(
        'email address',
        unique=True,
        db_index=True,
        max_length=254,
        help_text='Введите адрес электронной почты.',
        error_messages={
            'unique': "Пользователь с таким email уже существует.",
        },
    )
    first_name = models.CharField('first name', max_length=150)
    last_name = models.CharField('last name', max_length=150)
    avatar = models.ImageField('Аватар', upload_to='users/avatars/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.email


class Subscription(models.Model):
    """Модель подписки на автора."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )
    created = models.DateTimeField('Дата подписки', auto_now_add=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-created',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='cannot_subscribe_to_self'
            )
        ]

    def __str__(self):
        return f"{self.user.email} подписан на {self.author.email}"
