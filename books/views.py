from rest_framework import viewsets, permissions
from rest_framework.permissions import AllowAny

from books.models import Book
from books.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (AllowAny,)

    def get_permissions(self):
        if self.action in ("destroy", "update", "partial_update", "create"):
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return super().get_permissions()
