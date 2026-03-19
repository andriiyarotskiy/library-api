from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta, date
from decimal import Decimal

from books.models import Book
from borrowings.models import Borrowing


def sample_book(**params):
    defaults = {
        "title": "Sample Book",
        "author": "Sample Author",
        "inventory": 5,
        "daily_fee": Decimal("2.00"),
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


def sample_borrowing(user, **params):
    book = sample_book()
    defaults = {
        "book": book,
        "user": user,
        "expected_return_date": date.today() + timedelta(days=7),
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


class UnauthenticatedBorrowingApiTests(TestCase):
    """Test unauthenticated access to borrowings"""

    def setUp(self):
        self.client = APIClient()
        self.borrowings_url = "/borrowings/"

    def test_list_borrowings_forbidden(self):
        """Test that unauthenticated user cannot list borrowings (IsAuthenticated)"""
        res = self.client.get(self.borrowings_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_borrowing_forbidden(self):
        """Test that unauthenticated user cannot create borrowing"""
        book = sample_book()
        payload = {
            "book": book.id,
            "expected_return_date": date.today() + timedelta(days=7),
        }

        res = self.client.post(self.borrowings_url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    """Test authenticated user access to borrowings"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("user@test.com", "testpass123")
        self.user2 = get_user_model().objects.create_user(
            "user2@test.com", "testpass123"
        )
        self.client.force_authenticate(self.user)
        self.borrowings_url = "/borrowings/"

    def detail_url(self, borrowing_id):
        return f"/borrowings/{borrowing_id}/"

    def return_url(self, borrowing_id):
        return f"/borrowings/{borrowing_id}/return/"

    def test_list_own_borrowings(self):
        """Test user sees only own borrowings"""
        sample_borrowing(self.user)
        sample_borrowing(self.user)
        sample_borrowing(self.user2)  # other user's borrowing

        res = self.client.get(self.borrowings_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_create_borrowing_successful(self):
        """Test user can borrow book"""
        book = sample_book(inventory=3)
        payload = {
            "book": book.id,
            "expected_return_date": date.today() + timedelta(days=7),
        }

        res = self.client.post(self.borrowings_url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Verify serializer data
        self.assertIn("id", res.data)
        self.assertEqual(res.data["book"], book.id)

        # Verify inventory decreased
        book.refresh_from_db()
        self.assertEqual(book.inventory, 2)

        # Verify borrowing created with correct user
        borrowing = Borrowing.objects.get(id=res.data["id"])
        self.assertEqual(borrowing.user, self.user)

    def test_cannot_borrow_out_of_stock(self):
        """Test user cannot borrow book with 0 inventory"""
        book = sample_book(inventory=0)
        payload = {
            "book": book.id,
            "expected_return_date": date.today() + timedelta(days=7),
        }

        res = self.client.post(self.borrowings_url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", res.data)

    def test_cannot_borrow_with_past_return_date(self):
        """Test user cannot borrow with past return date"""
        book = sample_book()
        payload = {
            "book": book.id,
            "expected_return_date": date.today() - timedelta(days=1),
        }

        res = self.client.post(self.borrowings_url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("expected_return_date", res.data)

    def test_return_book_successful(self):
        """Test user can return book"""
        borrowing = sample_borrowing(self.user)
        initial_inventory = borrowing.book.inventory

        res = self.client.post(self.return_url(borrowing.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Verify inventory increased
        borrowing.book.refresh_from_db()
        self.assertEqual(borrowing.book.inventory, initial_inventory + 1)

        # Verify actual_return_date set
        borrowing.refresh_from_db()
        self.assertIsNotNone(borrowing.actual_return_date)

    def test_cannot_return_already_returned_book(self):
        """Test user cannot return already returned book"""
        borrowing = sample_borrowing(self.user, actual_return_date=date.today())

        res = self.client.post(self.return_url(borrowing.id))

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("actual_return_date", res.data)

    def test_filter_active_borrowings(self):
        """Test filter active borrowings by is_active=true"""
        active = sample_borrowing(self.user)
        returned = sample_borrowing(self.user, actual_return_date=date.today())

        res = self.client.get(self.borrowings_url, {"is_active": "true"})

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], active.id)

    def test_filter_returned_borrowings(self):
        """Test filter returned borrowings by is_active=false"""
        active = sample_borrowing(self.user)
        returned = sample_borrowing(self.user, actual_return_date=date.today())

        res = self.client.get(self.borrowings_url, {"is_active": "false"})

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], returned.id)


class AdminBorrowingApiTests(TestCase):
    """Test admin user access to borrowings"""

    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_superuser(
            "admin@test.com", "testpass123"
        )
        self.user1 = get_user_model().objects.create_user(
            "user1@test.com", "testpass123"
        )
        self.user2 = get_user_model().objects.create_user(
            "user2@test.com", "testpass123"
        )
        self.client.force_authenticate(self.admin)
        self.borrowings_url = "/borrowings/"

    def test_list_all_borrowings(self):
        """Test admin sees all borrowings"""
        sample_borrowing(self.user1)
        sample_borrowing(self.user1)
        sample_borrowing(self.user2)

        res = self.client.get(self.borrowings_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)

    def test_filter_by_user_id(self):
        """Test admin can filter borrowings by user_id"""
        sample_borrowing(self.user1)
        sample_borrowing(self.user1)
        sample_borrowing(self.user2)

        res = self.client.get(self.borrowings_url, {"user_id": self.user1.id})

        self.assertEqual(len(res.data), 2)

    def test_filter_by_user_id_shows_specific_user(self):
        """Test filter returns only specified user's borrowings"""
        borrowing3 = sample_borrowing(self.user2)

        res = self.client.get(self.borrowings_url, {"user_id": self.user2.id})

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], borrowing3.id)
