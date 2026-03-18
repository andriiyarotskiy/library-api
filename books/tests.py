from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from books.models import Book
from books.enums import Cover
from books.serializers import BookSerializer


def sample_book(**params):
    defaults = {
        "title": "Sample Book",
        "author": "Sample Author",
        "cover": Cover.SOFT,
        "inventory": 5,
        "daily_fee": Decimal("2.00"),
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


class UnauthenticatedBookApiTests(TestCase):
    """Test unauthenticated access"""

    def setUp(self):
        self.client = APIClient()
        self.books_url = "/books/"

    def detail_url(self, book_id):
        return f"/books/{book_id}/"

    def test_list_books_allowed(self):
        """Test that unauthenticated user can list books (AllowAny)"""
        sample_book()
        sample_book()

        res = self.client.get(self.books_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_book_allowed(self):
        """Test that unauthenticated user can retrieve book"""
        book = sample_book()

        res = self.client.get(self.detail_url(book.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = BookSerializer(book)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_forbidden(self):
        """Test that unauthenticated user gets 401 on create"""
        payload = {
            "title": "New Book",
            "author": "Author",
            "inventory": 5,
            "daily_fee": Decimal("2.00"),
        }
        res = self.client.post(self.books_url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookApiTests(TestCase):
    """Test authenticated non-admin user access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("user@test.com", "testpass123")
        self.client.force_authenticate(self.user)
        self.books_url = "/books/"

    def detail_url(self, book_id):
        return f"/books/{book_id}/"

    def test_list_books_allowed(self):
        """Test authenticated user can list books"""
        sample_book()
        sample_book()

        res = self.client.get(self.books_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_book_allowed(self):
        """Test authenticated user can retrieve book"""
        book = sample_book()

        res = self.client.get(self.detail_url(book.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = BookSerializer(book)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_forbidden(self):
        """Test that authenticated non-admin gets 403 on create"""
        payload = {
            "title": "New Book",
            "author": "Author",
            "inventory": 5,
            "daily_fee": Decimal("2.00"),
        }
        res = self.client.post(self.books_url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_forbidden(self):
        """Test that authenticated non-admin gets 403 on update"""
        book = sample_book()
        payload = {"inventory": 20}

        res = self.client.patch(self.detail_url(book.id), payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_forbidden(self):
        """Test that authenticated non-admin gets 403 on delete"""
        book = sample_book()

        res = self.client.delete(self.detail_url(book.id))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTests(TestCase):
    """Test admin user access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@test.com", "testpass123"
        )
        self.client.force_authenticate(self.user)
        self.books_url = "/books/"

    def detail_url(self, book_id):
        return f"/books/{book_id}/"

    def test_create_book_successful(self):
        """Test admin can create book"""
        payload = {
            "title": "Django Book",
            "author": "Real Python",
            "cover": Cover.HARD,
            "inventory": 10,
            "daily_fee": Decimal("3.50"),
        }

        res = self.client.post(self.books_url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Verify serializer data in response
        self.assertIn("id", res.data)
        self.assertEqual(res.data["title"], "Django Book")
        self.assertEqual(res.data["author"], "Real Python")
        self.assertEqual(res.data["cover"], Cover.HARD)
        self.assertEqual(res.data["inventory"], 10)
        self.assertEqual(float(res.data["daily_fee"]), 3.50)

        # Verify book in DB
        book = Book.objects.get(id=res.data["id"])
        for key, value in payload.items():
            self.assertEqual(value, getattr(book, key))

    def test_update_book_successful(self):
        """Test admin can update book"""
        book = sample_book()
        payload = {
            "title": "Updated Title",
            "inventory": 20,
        }

        res = self.client.patch(self.detail_url(book.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Verify serializer data includes updated fields
        self.assertEqual(res.data["title"], "Updated Title")
        self.assertEqual(res.data["inventory"], 20)
        self.assertEqual(res.data["author"], "Sample Author")  # unchanged

        # Verify DB updated
        book.refresh_from_db()
        self.assertEqual(book.title, "Updated Title")
        self.assertEqual(book.inventory, 20)

    def test_delete_book_successful(self):
        """Test admin can delete book"""
        book = sample_book()
        book_id = book.id

        res = self.client.delete(self.detail_url(book.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book_id).exists())

    def test_books_ordered_by_title(self):
        """Test that books list is ordered by title"""
        sample_book(title="Zebra Book")
        sample_book(title="Apple Book")
        sample_book(title="Monkey Book")

        res = self.client.get(self.books_url)

        titles = [book["title"] for book in res.data]
        self.assertEqual(titles, ["Apple Book", "Monkey Book", "Zebra Book"])
