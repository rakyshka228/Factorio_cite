from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Blueprint, Comment, Tag


class FactorioSiteTests(TestCase):
    def test_homepage_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_blueprint_detail_loads(self):
        response = self.client.get(reverse('blueprint_detail', args=['red']))
        self.assertEqual(response.status_code, 200)

    def test_user_can_publish_and_view_profile(self):
        response = self.client.post(reverse('register'), {
            'username': 'builder',
            'password1': 'A-strong-password-123',
            'password2': 'A-strong-password-123',
        })
        self.assertRedirects(response, reverse('home'))
        response = self.client.post(reverse('create_blueprint'), {
            'title': 'Моя фабрика',
            'description': 'Модульная схема производства.',
            'code': '0eNq-test',
            'tag_names': 'модули, производство',
        })
        self.assertEqual(response.status_code, 302)
        blueprint = Blueprint.objects.get(title='Моя фабрика')
        self.assertEqual(blueprint.author.username, 'builder')
        self.assertEqual(Tag.objects.count(), 2)
        self.assertEqual(self.client.get(reverse('profile', args=['builder'])).status_code, 200)

    def test_authenticated_user_can_like_and_comment(self):
        user = User.objects.create_user(username='builder', password='password')
        blueprint = Blueprint.objects.create(
            author=user,
            title='Тестовый чертёж',
            slug='testovyi-chertezh',
            description='Описание',
            code='code',
        )
        self.client.force_login(user)
        self.client.post(reverse('toggle_like', args=[blueprint.pk]))
        self.assertEqual(blueprint.likes.count(), 1)
        self.client.post(reverse('user_blueprint_detail', args=[blueprint.pk]), {
            'text': 'Работает отлично!',
        })
        self.assertEqual(Comment.objects.count(), 1)
