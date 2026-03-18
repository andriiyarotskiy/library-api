from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAppTest(TestCase):
    """Тести app User"""

    def test_create_user_with_email_successful(self):
        """Test of successful user creation with email"""
        email = "test@ExAmPlE.com"
        password = "testpass123"

        user = User.objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email.lower())
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_without_email_raises_error(self):
        """Test that creating a user without email causes an error"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="testpass123")

    def test_create_user_email_normalized(self):
        """Test that email normalizes (lowercase)"""
        email = "Test@EXAMPLE.COM"
        user = User.objects.create_user(email=email, password="testpass123")

        self.assertEqual(user.email, email.lower())

    def test_create_user_default_is_staff_false(self):
        """Default test is_staff=False"""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

        self.assertFalse(user.is_staff)

    def test_create_superuser_successful(self):
        """Test of successful creation of a superuser"""
        email = "admin@example.com"
        password = "adminpass123"

        user = User.objects.create_superuser(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password(password))

    def test_create_superuser_without_is_staff_raises_error(self):
        """Test that the superuser must have is_staff=True"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email="admin@example.com", password="testpass123", is_staff=False
            )

        self.assertIn("is_staff=True", str(context.exception))

    def test_create_superuser_without_is_superuser_raises_error(self):
        """Test that the superuser must have is_superuser=True"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email="admin@example.com", password="testpass123", is_superuser=False
            )

        self.assertIn("is_superuser=True", str(context.exception))

    def test_duplicate_email_raises_error(self):
        """Test that email must be unique"""
        email = "test@example.com"
        User.objects.create_user(email=email, password="testpass123")

        with self.assertRaises(Exception):  # IntegrityError
            User.objects.create_user(email=email, password="testpass123")

    def test_user_str_representation(self):
        """Test string user representation"""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

        # За замовчуванням Django повертає email
        self.assertEqual(str(user), "test@example.com")

    def test_username_field_is_email(self):
        """Test that USERNAME_FIELD set to email"""
        self.assertEqual(User.USERNAME_FIELD, "email")

    def test_required_fields_is_empty(self):
        """Test that REQUIRED_FIELDS empty (email is already required)"""
        self.assertEqual(User.REQUIRED_FIELDS, [])
