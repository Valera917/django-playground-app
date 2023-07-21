from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BookSerializer


class BookTestAPI(APITestCase):
    def test_get(self):
        book_1 = Book.objects.create(name='test_1', price=25.5)
        book_2 = Book.objects.create(name='test_2', price=266.5)
        url = reverse('book-list')
        response = self.client.get(url)
        serialized_data = BookSerializer([book_1, book_2], many=True).data
        self.assertEqual(response.data, serialized_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
