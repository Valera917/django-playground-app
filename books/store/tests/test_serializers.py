from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg, Exists, OuterRef
from django.test import TestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def test_correct_data(self):
        user_1 = User.objects.create(username='test_username_1')
        user_2 = User.objects.create(username='test_username_2')
        user_3 = User.objects.create(username='test_username_3')

        book_1 = Book.objects.create(name='test_1', price=25.5, author_name="Valera")
        book_2 = Book.objects.create(name='test_2', price=266.5, author_name="Valera")

        UserBookRelation.objects.create(user=user_1, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user_2, book=book_1, like=True, rate=4)
        UserBookRelation.objects.create(user=user_3, book=book_1, like=True, rate=5)

        UserBookRelation.objects.create(user=user_1, book=book_2, like=True, rate=3)
        UserBookRelation.objects.create(user=user_2, book=book_2, like=True, rate=4)
        UserBookRelation.objects.create(user=user_3, book=book_2, like=False)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate'),
        ).order_by('id')
        data = BookSerializer(books, many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'test_1',
                'price': '25.50',
                'author_name': 'Valera',
                'annotated_likes': 3,
                'rating': '4.67',
            },
            {
                'id': book_2.id,
                'name': 'test_2',
                'price': '266.50',
                'author_name': 'Valera',
                'annotated_likes': 2,
                'rating': '3.50',
            },
        ]
        self.assertEqual(data, expected_data)
