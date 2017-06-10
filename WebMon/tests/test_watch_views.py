from datetime import timedelta, datetime

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Watch
from ..serializers import WatchSerializer


class GetWatchesTest(APITestCase):
    """
    Test module for retrieving Watches API
    """

    def setUp(self):
        self.user1 = User.objects.create(username='test_user', password='test_pass')
        self.user2 = User.objects.create(username='another_user', password='pass_pass')
        self.watch1 = Watch.objects.create(name='watch1', url='http://example.com/test1', xpath='/books[1]',
                                           period=timedelta(hours=5), notify=False, owner=self.user1)
        self.watch2 = Watch.objects.create(name='watch2', url='http://example.com/test2', xpath='/books[2]',
                                           period=timedelta(days=1), notify=True, owner=self.user1)
        self.watch3 = Watch.objects.create(name='watch3', url='http://example.com/test3', xpath='/books[3]',
                                           period=timedelta(hours=7), notify=False, owner=self.user2)
        self.watch4 = Watch.objects.create(name='watch4', url='http://example.com/test4', xpath='/books[4]',
                                           period=timedelta(hours=12), notify=False, owner=self.user2)

    def test_get_authenticated_user_watches(self):
        url = reverse('watch-list')
        watches = self.user1.watches.all()
        serializer = WatchSerializer(watches, many=True)

        self.client.force_login(self.user1)

        response = self.client.get(url)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_unauthenticated_user_watches(self):
        url = reverse('watch-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_valid_authenticated_watch(self):
        url = reverse('watch-detail', kwargs={'pk': self.watch1.pk})
        serializer = WatchSerializer(self.watch1)

        self.client.force_login(self.user1)
        response = self.client.get(url)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_valid_unauthenticated_watch(self):
        url = reverse('watch-detail', kwargs={'pk': self.watch1.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_valid_watch_wrong_user(self):
        url = reverse('watch-detail', kwargs={'pk': self.watch1.pk})

        self.client.force_login(self.user2)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_invalid_watch(self):
        url = reverse('watch-detail', kwargs={'pk': 30})

        self.client.force_login(self.user1)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AddWatchesTest(APITestCase):
    """
    Test module for creating new Watches.
    """
    def setUp(self):
        self.user1 = User.objects.create(username='test_user', password='test_pass')
        self.user2 = User.objects.create(username='another_user', password='pass_pass')
        self.new_watch_data = {
            'name': 'NewWatch',
            'url': 'http://example.com',
            'xpath': '/bookstore/book[1]',
            'period': timedelta(hours=1, minutes=15),
            'notify': True
        }
        self.url = reverse('watch-list')

    def test_add_authenticated_watch(self):
        self.client.force_login(self.user1)
        response = self.client.post(self.url, data=self.new_watch_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        watch = Watch.objects.get()
        self.assertEqual(watch.name, 'NewWatch', "name was not set")
        self.assertEqual(watch.url, 'http://example.com', "url was not set")
        self.assertEqual(watch.xpath, '/bookstore/book[1]', "xpath was not set")
        self.assertEqual(watch.period, timedelta(hours=1, minutes=15), "period was not set")
        self.assertEqual(watch.notify, True, "notify was not set")
        self.assertEqual(watch.owner, self.user1, "owner was not set")

    def test_add_authenticated_watch_validation(self):
        self.client.force_login(self.user1)

        new_watch_data1 = self.new_watch_data
        new_watch_data1['name'] = ''
        response = self.client.post(self.url, data=new_watch_data1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "Name not validated")

        new_watch_data2 = self.new_watch_data
        new_watch_data2['url'] = ''
        response = self.client.post(self.url, data=new_watch_data2)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "URL not validated")

        new_watch_data3 = self.new_watch_data
        new_watch_data3['xpath'] = ''
        response = self.client.post(self.url, data=new_watch_data3)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "XPath not validated")

        new_watch_data4 = self.new_watch_data
        new_watch_data4['period'] = None
        response = self.client.post(self.url, data=new_watch_data4)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "Period not validated")

    def test_add_unauthenticated_watch(self):
        response = self.client.post(self.url, data=self.new_watch_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Watch.objects.count(), 0)

    def test_next_check_is_set_correctly(self):
        self.client.force_login(self.user1)

        next_check = datetime.now() + timedelta(hours=1, minutes=15)
        response = self.client.post(self.url, data=self.new_watch_data)
        watch = Watch.objects.get()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(int(watch.next_check.timestamp()), int(next_check.timestamp()))


class UpdateWatchTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='test_user', password='test_pass')
        self.watch1 = Watch.objects.create(name='watch1', url='http://example.com/test1', xpath='/books[1]',
                                           period=timedelta(hours=5), notify=False, owner=self.user1)
        self.url = reverse('watch-detail', kwargs={'pk': self.watch1.pk})
        self.new_watch_data = {
            'name': 'w12',
            'url': 'http://example.com/test21',
            'xpath': '/table[1]',
            'period': timedelta(hours=10),
            'notify': True
        }

    def test_update_authorized_watch(self):
        """Test updating Watch fields.
        `next_check` value should not change.
        """
        old_next_check = self.watch1.next_check

        self.client.force_login(self.user1)
        response = self.client.put(self.url, self.new_watch_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        watch2 = Watch.objects.get()
        self.assertEqual(watch2.name, self.new_watch_data['name'], "name was not updated")
        self.assertEqual(watch2.url, self.new_watch_data['url'], "url was not updated")
        self.assertEqual(watch2.xpath, self.new_watch_data['xpath'], "xpath was not updated")
        self.assertEqual(watch2.period, self.new_watch_data['period'], "period was not updated")
        self.assertEqual(watch2.next_check, old_next_check, "next_check was updated")
        self.assertEqual(watch2.notify, self.new_watch_data['notify'], "notify was not updated")

    def test_update_unauthorized_watch(self):
        response = self.client.put(self.url, self.new_watch_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_invalid_watch(self):
        url = reverse('watch-detail', kwargs={'pk': 30})
        self.client.force_login(self.user1)
        response = self.client.put(url, self.new_watch_data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_authorized_watch_validation(self):
        self.client.force_login(self.user1)

        bad_watch_data = self.new_watch_data
        bad_watch_data['name'] = ''
        response = self.client.put(self.url, data=bad_watch_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        bad_watch_data = self.new_watch_data
        bad_watch_data['url'] = ''
        response = self.client.put(self.url, data=bad_watch_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        bad_watch_data = self.new_watch_data
        bad_watch_data['xpath'] = ''
        response = self.client.put(self.url, data=bad_watch_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        bad_watch_data = self.new_watch_data
        bad_watch_data['period'] = None
        response = self.client.put(self.url, data=bad_watch_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteWatchTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='test_user', password='test_pass')
        self.watch1 = Watch.objects.create(name='watch1', url='http://example.com/test1', xpath='/books[1]',
                                           period=timedelta(hours=5), notify=False, owner=self.user1)
        self.url = reverse('watch-detail', kwargs={'pk': self.watch1.pk})

    def test_delete_authorized_watch(self):
        self.client.force_login(self.user1)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Watch.objects.count(), 0)

    def test_delete_unauthorized_watch(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Watch.objects.count(), 1)

    def test_delete_invalid_watch(self):
        url = reverse('watch-detail', kwargs={'pk': 30})

        self.client.force_login(self.user1)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
