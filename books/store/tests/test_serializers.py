from django.test import TestCase

from store.models import Book
from store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def test_correct_data(self):
        book_1 = Book.objects.create(name='test_1', price=25.5, author_name="Valera")
        book_2 = Book.objects.create(name='test_2', price=266.5, author_name="Valera")
        data = BookSerializer([book_1, book_2], many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'test_1',
                'price': '25.50',
                'author_name': 'Valera'
            },
            {
                'id': book_2.id,
                'name': 'test_2',
                'price': '266.50',
                'author_name': 'Valera'
            },
        ]
        self.assertEqual(data, expected_data)
