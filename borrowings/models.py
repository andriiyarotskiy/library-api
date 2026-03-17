from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models

from books.models import Book
from configs import settings


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )

    class Meta:
        ordering = ("expected_return_date",)

    def __str__(self):
        return f"{self.borrow_date} - {self.expected_return_date}"

    @staticmethod
    def validate_return_date(return_date, error_to_raise):
        today_date = datetime.today().date()
        if return_date <= today_date:
            raise error_to_raise(
                {
                    "expected_return_date": "The return date must be after the borrowing date"
                }
            )

    @staticmethod
    def validate_book_inventory(book, error_to_raise):
        inventory = getattr(book, "inventory")
        title = getattr(book, "title")
        if inventory <= 0:
            raise error_to_raise(
                {
                    "error": f'The book "{title}" is not yet available in the library, '
                    f"you need to expect a return from other users"
                }
            )

    def clean(self):
        self.validate_return_date(self.expected_return_date, ValidationError)
        self.validate_book_inventory(self.book, ValidationError)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
