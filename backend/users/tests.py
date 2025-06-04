from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from recipes.models import Subscription

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты модели User"""
    
    def test_user_creation(self):
        """Тест создания пользователя"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_str(self):
        """Тест строкового представления пользователя"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(str(user), 'Test User')


class UserAPITest(APITestCase):
    """Тесты API пользователей"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            first_name='User',
            last_name='One',
            password='testpass123'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            first_name='User',
            last_name='Two',
            password='testpass123'
        )
        
        self.token = Token.objects.create(user=self.user1)
    
    def test_user_list(self):
        """Тест получения списка пользователей"""
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_user_detail(self):
        """Тест получения детальной информации о пользователе"""
        url = reverse('user-detail', kwargs={'pk': self.user1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user1')
    
    def test_user_me_authenticated(self):
        """Тест получения информации о себе для авторизованного пользователя"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        url = reverse('user-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user1')
    
    def test_user_me_anonymous(self):
        """Тест получения информации о себе для анонимного пользователя"""
        url = reverse('user-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_registration(self):
        """Тест регистрации нового пользователя"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123'
        }
        
        url = reverse('user-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_subscription_create(self):
        """Тест создания подписки"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        url = reverse('user-subscribe', kwargs={'pk': self.user2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Subscription.objects.filter(user=self.user1, author=self.user2).exists())
    
    def test_subscription_delete(self):
        """Тест удаления подписки"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Создаем подписку
        Subscription.objects.create(user=self.user1, author=self.user2)
        
        url = reverse('user-subscribe', kwargs={'pk': self.user2.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Subscription.objects.filter(user=self.user1, author=self.user2).exists())
    
    def test_subscriptions_list(self):
        """Тест получения списка подписок"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Создаем подписку
        Subscription.objects.create(user=self.user1, author=self.user2)
        
        url = reverse('user-subscriptions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], 'user2')
    
    def test_self_subscription_forbidden(self):
        """Тест запрета подписки на самого себя"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        url = reverse('user-subscribe', kwargs={'pk': self.user1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_duplicate_subscription_forbidden(self):
        """Тест запрета повторной подписки"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Создаем подписку
        Subscription.objects.create(user=self.user1, author=self.user2)
        
        url = reverse('user-subscribe', kwargs={'pk': self.user2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SubscriptionModelTest(TestCase):
    """Тесты модели Subscription"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            first_name='User',
            last_name='One'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            first_name='User',
            last_name='Two'
        )
    
    def test_subscription_creation(self):
        """Тест создания подписки"""
        subscription = Subscription.objects.create(
            user=self.user1,
            author=self.user2
        )
        
        self.assertEqual(subscription.user, self.user1)
        self.assertEqual(subscription.author, self.user2)
    
    def test_subscription_str(self):
        """Тест строкового представления подписки"""
        subscription = Subscription.objects.create(
            user=self.user1,
            author=self.user2
        )
        
        expected = f"{self.user1.username} подписан на {self.user2.username}"
        self.assertEqual(str(subscription), expected)
    
    def test_subscription_unique_constraint(self):
        """Тест уникальности подписки"""
        Subscription.objects.create(user=self.user1, author=self.user2)
        
        # Попытка создать дублирующую подписку
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Subscription.objects.create(user=self.user1, author=self.user2)
