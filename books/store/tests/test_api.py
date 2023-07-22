from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BookSerializer


class BookTestAPI(APITestCase):
    def setUp(self):
        self.book_1 = Book.objects.create(name='test_1', price=25.5, author_name="Valera-1")
        self.book_2 = Book.objects.create(name='test_2 Valera-1', price=450, author_name="Valera-2")
        self.book_3 = Book.objects.create(name='test_3', price=320, author_name="Valera-3")

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serialized_data = BookSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        self.assertEqual(response.data, serialized_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
