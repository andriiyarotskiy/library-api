from datetime import datetime

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        data = super().validate(attrs=attrs)

        Borrowing.validate_return_date(data["expected_return_date"], ValidationError)
        Borrowing.validate_book_inventory(data["book"], ValidationError)

        return data

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        )
        read_only_fields = ("id", "actual_return_date")

    @transaction.atomic
    def create(self, validated_data):
        book = validated_data.pop("book")
        book.inventory -= 1
        book.save()
        return Borrowing.objects.create(book=book, **validated_data)


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)


class BorrowingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        )


class BorrowingReturnSerializer(serializers.Serializer):
    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        if self.instance.actual_return_date is not None:
            raise ValidationError(
                {"actual_return_date": "The book was already returned"}
            )
        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        book = instance.book
        book.inventory += 1
        book.save()

        instance.actual_return_date = datetime.today().strftime("%Y-%m-%d")
        instance.save()

        return instance
