from datetime import timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from WebMon.models import Watch, Value
from WebMon.serializers import ValueSerializer


class GetWatchValues(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='test_user', password='test_pass')
        self.user2 = User.objects.create(username='second_user', password='test_test')
        self.watch1 = Watch.objects.create(name='watch1', url='http://example.com/test1', xpath='/books[1]',
                                           period=timedelta(hours=5), notify=False, owner=self.user1)
        self.value1 = Value.objects.create(watch=self.watch1, content="2.3.7")
        self.value2 = Value.objects.create(watch=self.watch1, content="2.4.5")

    def test_get_authorized_latest_watch_value(self):
        url = reverse('watch-value-latest', kwargs={'pk': self.watch1.pk})
        serializer = ValueSerializer(self.value2)

        self.client.force_login(self.user1)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_unauthorized_latest_watch_value(self):
        url = reverse('watch-value-latest', kwargs={'pk': self.watch1.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_invalid_watch_latest_value(self):
        url = reverse('watch-value-latest', kwargs={'pk': 30})

        self.client.force_login(self.user1)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_authorized_watch_values_list(self):
        url = reverse('watch-value-list', kwargs={'pk': self.watch1.pk})
        values = self.watch1.values.all()
        serializer = ValueSerializer(values, many=True)

        self.client.force_login(self.user1)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_wrong_user_watch_latest_value(self):
        url = reverse('watch-value-latest', kwargs={'pk': self.watch1.pk})

        self.client.force_login(self.user2)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_invalid_watch_value_list(self):
        url = reverse('watch-value-list', kwargs={'pk': 30})

        self.client.force_login(self.user1)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
