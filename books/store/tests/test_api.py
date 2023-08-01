from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BookTestAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.book_1 = Book.objects.create(name='test_1', price=25.5, author_name="Valera-1", owner=self.user)
        self.book_2 = Book.objects.create(name='test_2 Valera-1', price=450, author_name="Valera-2", owner=self.user)
        self.book_3 = Book.objects.create(name='test_3', price=320, author_name="Valera-3", owner=self.user)

    def test_get_books(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serialized_data = BookSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        self.assertEqual(response.data, serialized_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_book(self):
        url = reverse('book-detail', args=(self.book_1.id, ))
        response = self.client.get(url)
        serialized_data = BookSerializer(self.book_1).data
        self.assertEqual(response.data, serialized_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book(self):
        url = reverse('book-list')
        payload = {
            'name': 'test_post',
            'price': Decimal('25.5'),
            'author_name': "Valera-1"
        }
        self.client.force_login(self.user)
        response = self.client.post(url, data=payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=response.data['id'])
        for key, value in payload.items():
            self.assertEqual(getattr(book, key), value)
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update_book(self):
        url = reverse('book-detail', args=(self.book_1.id, ))
        payload = {
            'name': 'updated_post',
            'price': Decimal('65.00'),
            'author_name': 'Valeraqaaa'
        }
        self.client.force_login(self.user)
        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book_1.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(self.book_1, key), value)

    def test_update_book_not_owner(self):
        self.user2 = User.objects.create(username="test_user2")
        url = reverse('book-detail', args=(self.book_1.id, ))
        payload = {
            'name': 'updated_post',
            'price': Decimal('65.00'),
            'author_name': 'Valeraqaaa'
        }
        self.client.force_login(self.user2)
        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)
        self.book_1.refresh_from_db()
        self.assertEqual(self.book_1.price, Decimal(25.5))

    def test_update_book_staff(self):
        self.user2 = User.objects.create(username="test_user2", is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        payload = {
            'name': 'updated_post',
            'price': Decimal('65.00'),
            'author_name': 'Valeraqaaa'
        }
        self.client.force_login(self.user2)
        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book_1.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(self.book_1, key), value)

    def test_delete_book(self):
        self.client.force_login(self.user)

        url = reverse('book-detail', args=(self.book_1.id, ))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=self.book_1.id).exists())

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 450})
        serialized_data = BookSerializer([self.book_2], many=True).data
        self.assertEqual(response.data, serialized_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Valera-1'})
        serialized_data = BookSerializer([self.book_1,
                                          self.book_2], many=True).data
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data, serialized_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_ordering(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'price'})
        serialized_data = BookSerializer([self.book_1,
                                          self.book_3,
                                          self.book_2], many=True).data
        self.assertEqual(response.data, serialized_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BookRelationAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.user2 = User.objects.create(username="test_user2")
        self.book_1 = Book.objects.create(name='test_1', price=25.5, author_name="Valera-1", owner=self.user)
        self.book_2 = Book.objects.create(name='test_2 Valera-1', price=450, author_name="Valera-2", owner=self.user)

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id, ))
        payload = {
            'like': True,
        }
        self.client.force_login(self.user)
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.like)

        payload = {
            'in_bookmarks': True,
        }
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id, ))
        payload = {
            'rate': 3,
        }
        self.client.force_login(self.user)
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual(relation.rate, 3)

    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id, ))
        payload = {
            'rate': 7,
        }
        self.client.force_login(self.user)
        response = self.client.patch(url, payload)

        self.assertEqual({'rate': [ErrorDetail(string='"7" is not a valid choice.', code='invalid_choice')]}, response.data)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual(relation.rate, None)

