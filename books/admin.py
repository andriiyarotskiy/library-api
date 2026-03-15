from django.contrib import admin
from django.contrib.auth.models import Group

from books.models import Book

admin.site.register(Book)
admin.site.unregister(Group)
