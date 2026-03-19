from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from books.models import Book
from books.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action in ("destroy", "update", "partial_update", "create"):
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]
