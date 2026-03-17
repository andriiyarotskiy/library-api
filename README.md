# Library Management System - Development Tasks

[doc](https://docs.google.com/document/d/1wkWketx6ROKlrfpUqKJEJhS8EzVe3BOX/edit#heading=h.cdjaa0qni1m6/)

A comprehensive guide for implementing a Library Management System with Django REST Framework, featuring Books, Users, Borrowing, and Payment services with JWT authentication and role-based permissions.

---

## Resources

### 1. Book
- **Title**: str
- **Author**: str
- **Cover**: Enum: `HARD` | `SOFT`
- **Inventory**: positive int (number of this specific book available in the library)
- **Daily fee**: decimal in $USD

### 2. User (Customer)
- **Email**: str
- **First name**: str
- **Last name**: str
- **Password**: str
- **Is staff**: bool

### 3. Borrowing
- **Borrow date**: date
- **Expected return date**: date
- **Actual return date**: date
- **Book id**: int
- **User id**: int

### 4. Payment
- **Status**: Enum: `PENDING` | `PAID`
- **Type**: Enum: `PAYMENT` | `FINE`
- **Borrowing id**: int
- **Session url**: URL (Stripe payment session URL)
- **Session id**: str (Stripe payment session ID)
- **Money to pay**: decimal in $USD (calculated borrowing total price)

---

## Components

### 1. Books Service
Managing the quantity of books (CRUD for Books)

#### API Endpoints:
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `books/` | Add new book |
| GET | `books/` | Get a list of books |
| GET | `books/<id>/` | Get book detail info |
| PUT/PATCH | `books/<id>/` | Update book (also manage inventory) |
| DELETE | `books/<id>/` | Delete book |

#### Tasks:
1. **Initialize the books app**
   - Create a new Django app named `books`
   - Add the app to `INSTALLED_APPS` in settings
   - Create the necessary app structure (models, serializers, views, urls)

2. **Add the book model**
   - Create a `Book` model with fields:
     - `title` (CharField)
     - `author` (CharField)
     - `cover` (CharField with choices: HARD, SOFT)
     - `inventory` (PositiveIntegerField)
     - `daily_fee` (DecimalField)

3. **Add permissions to the Books Service**
   - Only admin (is_staff) users can create/update/delete books
   - All users (even unauthenticated ones) should be able to list and retrieve books
   - Use JWT token authentication from the Users service

4. **Implement the serializer & views for all the endpoints**
   - Create a `BookSerializer` for serializing book data
   - Implement a `BookViewSet` with list, create, retrieve, update, partial_update, and destroy methods
   - Register the viewset in `urls.py` using a router

---

### 2. Users Service
Managing authentication & user registration

#### API Endpoints:
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `users/` | Register a new user |
| POST | `users/token/` | Get JWT tokens (access + refresh) |
| POST | `users/token/refresh/` | Refresh JWT token |
| GET | `users/me/` | Get my profile info |
| PUT/PATCH | `users/me/` | Update profile info |

#### Tasks:
1. **Initialize the users app**
   - Create a new Django app named `users`
   - Add the app to `INSTALLED_APPS` in settings
   - Create the necessary app structure (models, serializers, views, urls)

2. **Add the user model with email**
   - Extend Django's `AbstractUser` model
   - Fields:
     - `email` (EmailField, unique)
     - `first_name` (CharField)
     - `last_name` (CharField)
     - `password` (handled by AbstractUser)
     - `is_staff` (BooleanField, default=False)

3. **Add JWT support**
   - Install and configure `djangorestframework-simplejwt`
   - Create JWT token endpoints for obtaining and refreshing tokens
   - Configure token settings (expiration times, algorithm, etc.)
   - For better experience with ModHeader Chrome extension, change the default `Authorization` header to `Authorize`

4. **Implement the serializer & views for all the endpoints**
   - Create a `UserSerializer` for user data
   - Create a `UserRegistrationSerializer` for user registration
   - Implement endpoints for:
     - User registration (POST `users/`)
     - JWT token obtain (POST `users/token/`)
     - JWT token refresh (POST `users/token/refresh/`)
     - Get current user profile (GET `users/me/`)
     - Update current user profile (PUT/PATCH `users/me/`)

---

### 3. Borrowings Service
Managing users' borrowings of books

#### API Endpoints:
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `borrowings/` | Add new borrowing (inventory should be -= 1) |
| GET | `borrowings/?user_id=...&is_active=...` | Get borrowings by user id and active status |
| GET | `borrowings/<id>/` | Get specific borrowing |
| POST | `borrowings/<id>/return/` | Set actual return date (inventory should be += 1) |

#### Tasks:
1. **Initialize the borrowings app**
   - Create a new Django app named `borrowings`
   - Add the app to `INSTALLED_APPS` in settings
   - Create the necessary app structure (models, serializers, views, urls)

2. **Add the borrowing model with constraints**
   - Create a `Borrowing` model with fields:
     - `user` (ForeignKey to User, on_delete=CASCADE)
     - `book` (ForeignKey to Book, on_delete=CASCADE)
     - `borrow_date` (DateField, auto_now_add=True)
     - `expected_return_date` (DateField)
     - `actual_return_date` (DateField, null=True, blank=True)
   - Add model constraints:
     - `borrow_date` cannot be in the future
     - `expected_return_date` must be after `borrow_date`
     - `actual_return_date` (if provided) must be after `borrow_date` and cannot exceed today's date

3. **Implement the Borrowing List & Detail endpoint**
   - Create a `BorrowingReadSerializer` that includes:
     - All borrowing fields
     - Nested book details
     - User information
   - Implement list and retrieve endpoints
   - Apply permissions: only authenticated users can access
   - Non-admin users can see only their own borrowings
   - Admin users can see all borrowings

4. **Implement the Create Borrowing endpoint**
   - Create a `BorrowingCreateSerializer` with fields:
     - `book` (PrimaryKeyRelatedField)
     - `expected_return_date` (DateField)
   - Validate book inventory is not 0
   - Decrease inventory by 1 for book
   - Attach the current user to the borrowing
   - Implement create endpoint with authentication

5. **Add filtering for the Borrowings List endpoint**
   - Filter by `user_id` (admin only: can see specific user's borrowings or all; non-admin: only their own)
   - Filter by `is_active` (true for active borrowings, false for completed, omit for all)
   - Ensure each non-admin can see only their own borrowings
   - Require authentication for list endpoint

6. **Implement the Return Borrowing endpoint**
   - Create `borrowings/<id>/return/` endpoint
   - Set the `actual_return_date` to today's date
   - Increase inventory by 1 for the book
   - Only the user who borrowed the book or admin can perform this action

---

### 4. Payments Service (Optional/Future)
Managing payment transactions for book borrowing

#### Key Points:
- Track payment status (PENDING, PAID)
- Track payment type (PAYMENT, FINE)
- Integrate with Stripe for payment processing
- Store Stripe session information
- Calculate total borrowing cost based on daily fee and number of days

---

## Development Tasks Summary

### Phase 1: Books Service
- [ ] Initialize books app
- [ ] Create Book model
- [ ] Create BookSerializer
- [ ] Create BookViewSet with CRUD operations
- [ ] Add permission classes (IsAdmin for write operations)
- [ ] Register endpoints in urls.py

### Phase 2: Users Service
- [ ] Initialize users app
- [ ] Create custom User model extending AbstractUser
- [ ] Install djangorestframework-simplejwt
- [ ] Configure JWT authentication with custom header
- [ ] Create UserSerializer and UserRegistrationSerializer
- [ ] Create JWT token endpoints
- [ ] Create user profile endpoints (GET/PUT/PATCH `/users/me/`)
- [ ] Register endpoints in urls.py

### Phase 3: Borrowings Service
- [ ] Initialize borrowings app
- [ ] Create Borrowing model with constraints
- [ ] Create BorrowingReadSerializer
- [ ] Create BorrowingCreateSerializer
- [ ] Create BorrowingViewSet with list and retrieve methods
- [ ] Implement create endpoint with inventory management
- [ ] Implement return endpoint (POST `/borrowings/<id>/return/`)
- [ ] Add filtering (user_id, is_active)
- [ ] Register endpoints in urls.py

### Phase 4: Testing & Documentation
- [ ] Write unit tests for each service
- [ ] Write integration tests
- [ ] Document API endpoints
- [ ] Test authentication and permissions

---

## Installation & Setup

```bash
# Clone the repository
git clone <repository-url>

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create a superuser (admin)
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

---

## Key Implementation Notes

### JWT Authentication
- Use `djangorestframework-simplejwt` for JWT token management
- Custom header: Use `Authorize` instead of `Authorization` for better tool compatibility
- Access tokens should have shorter expiration, refresh tokens longer
- Tokens should be sent in the request header: `Authorize: <token>`

### Inventory Management
- When creating a borrowing: `book.inventory -= 1`
- When returning a borrowing: `book.inventory += 1`
- Use database transactions to ensure data consistency
- Validate inventory > 0 before allowing borrowing

### Permissions
- Books: Read is public, write is admin-only
- Users: Registration is public, profile access is authenticated users only
- Borrowings: Authenticated users only, non-admin see only their own

### Filtering
- Use Django Filter or implement custom filtering
- `is_active` parameter filters by `actual_return_date` (null vs not null)
- `user_id` parameter for admin users to filter by specific user

---

## References

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [djangorestframework-simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Django Models](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [Stripe API Documentation](https://stripe.com/docs/api)

---

**Last Updated**: March 2026