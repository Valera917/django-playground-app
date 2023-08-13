from unittest.mock import patch

from _decimal import Decimal
from django.contrib.auth.models import User
from django_filters.compat import TestCase

from store.models import Book, UserBookRelation
from store.services import set_rating


class SetRaTingTestCase(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='test_username_1', first_name='test_first_name_1', last_name='test_last_name_1')
        self.user_2 = User.objects.create(username='test_username_2', first_name='test_first_name_2', last_name='test_last_name_2')
        self.user_3 = User.objects.create(username='test_username_3', first_name='1', last_name='2')

        self.book_1 = Book.objects.create(name='test_1', price=25.5, author_name="Valera", owner=self.user_1)

        UserBookRelation.objects.create(user=self.user_1, book=self.book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=self.user_2, book=self.book_1, like=True, rate=4)
        UserBookRelation.objects.create(user=self.user_3, book=self.book_1, like=True, rate=5)

    def test_calculate_average_rating(self):
        set_rating(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual(self.book_1.rating, Decimal('4.67'))

    @patch("store.services.set_rating")
    def test_set_rating_called_when_condition_met(self, mock_set_rating):
        relation = UserBookRelation(user=self.user_1, book=self.book_1)
        relation.rate = 2
        relation.save()

        mock_set_rating.assert_called_once_with(self.book_1)

    @patch("store.services.set_rating")
    def test_set_rating_not_called_when_condition_not_met(self, mock_set_rating):
        relation = UserBookRelation.objects.get(user=self.user_1, book=self.book_1)
        relation.rate = 5
        relation.save()

        mock_set_rating.assert_not_called()
