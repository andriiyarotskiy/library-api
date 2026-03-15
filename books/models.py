from django.db import models

from books.enums import Cover


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.IntegerField(choices=Cover, default=Cover.SOFT)
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return self.title
