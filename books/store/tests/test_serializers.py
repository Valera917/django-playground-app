from _decimal import Decimal
from django.contrib.auth.models import User
from django.db.models import Count, Case, When, F
from django.test import TestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def test_correct_data(self):
        user_1 = User.objects.create(username='test_username_1',
                                     first_name='test_first_name_1',
                                     last_name='test_last_name_1')
        user_2 = User.objects.create(username='test_username_2',
                                     first_name='test_first_name_2',
                                     last_name='test_last_name_2')
        user_3 = User.objects.create(username='test_username_3',
                                     first_name='1',
                                     last_name='2')

        book_1 = Book.objects.create(name='test_1', price=25.5, author_name="Valera", owner=user_1)
        book_2 = Book.objects.create(name='test_2', price=266.5, author_name="Valera")

        UserBookRelation.objects.create(user=user_1, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user_2, book=book_1, like=True, rate=4)
        user_book_3 = UserBookRelation.objects.create(user=user_3, book=book_1, like=True)
        user_book_3.rate = 4
        user_book_3.save()

        UserBookRelation.objects.create(user=user_1, book=book_2, like=True, rate=3)
        UserBookRelation.objects.create(user=user_2, book=book_2, like=True, rate=4)
        UserBookRelation.objects.create(user=user_3, book=book_2, like=False)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            owner_name=F('owner__username'),
        ).order_by('id')
        data = BookSerializer(books, many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'test_1',
                'price': '25.50',
                'author_name': 'Valera',
                'annotated_likes': 3,
                'rating': '4.33',
                'owner_name': user_1.username,
                'readers': [
                    {
                        'first_name': 'test_first_name_1',
                        'last_name': 'test_last_name_1',
                    },
                    {
                        'first_name': 'test_first_name_2',
                        'last_name': 'test_last_name_2',
                    },
                    {
                        'first_name': '1',
                        'last_name': '2',
                    },
                ]
            },
            {
                'id': book_2.id,
                'name': 'test_2',
                'price': '266.50',
                'author_name': 'Valera',
                'annotated_likes': 2,
                'rating': '3.50',
                'owner_name': None,
                'readers': [
                    {
                        'first_name': 'test_first_name_1',
                        'last_name': 'test_last_name_1',
                    },
                    {
                        'first_name': 'test_first_name_2',
                        'last_name': 'test_last_name_2',
                    },
                    {
                        'first_name': '1',
                        'last_name': '2',
                    },
                ]
            },
        ]
        self.assertEqual(data, expected_data)
