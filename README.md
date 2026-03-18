# 📚 Library Management API

A simple REST API for managing a library's book inventory and tracking user borrowings.

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** (tested with Python 3.11.14)
- pip

### Step-by-Step Installation

```bash

# 1. Clone the repository
git clone <your-repo-url>
cd library-api

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# 4. Upgrade pip (recommended)
pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt

# 6. Apply database migrations
python manage.py migrate

# 7. Create admin user (superuser)
python manage.py createsuperuser
# Follow prompts to enter email and password

# 8. Run development server
python manage.py runserver
```

✅ **Server is running at:** `http://127.0.0.1:8000/`

### Verify Installation

Test if everything works:

```bash

# 1. List all books (public endpoint)
curl http://127.0.0.1:8000/books/

# 2. View interactive API documentation
# Open in browser: http://127.0.0.1:8000/api/swagger/

# 3. Access Django admin panel
# Open in browser: http://127.0.0.1:8000/admin/
```

---

## 📖 API Overview

### Authentication
All protected endpoints require JWT token authentication.

**Get Token:**
```bash

POST /users/token/
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Response:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

Add the access token to requests via header:
```
Authorization: Bearer <your_access_token>
```

---

## 📚 Endpoints

### Users
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| POST | `/users/` | Register new user | ❌ |
| POST | `/users/token/` | Get JWT tokens | ❌ |
| POST | `/users/token/refresh/` | Refresh access token | ❌ |
| GET | `/users/me/` | Get your profile | ✅ |
| PUT/PATCH | `/users/me/` | Update your profile | ✅ |

### Books
| Method | Endpoint | Description | Auth Required | Admin Only |
|--------|----------|-------------|---|---|
| GET | `/books/` | List all books | ❌ | ❌ |
| GET | `/books/{id}/` | Get book details | ❌ | ❌ |
| POST | `/books/` | Create book | ✅ | ✅ |
| PUT | `/books/{id}/` | Update book | ✅ | ✅ |
| DELETE | `/books/{id}/` | Delete book | ✅ | ✅ |

### Borrowings
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| GET | `/borrowings/` | List your borrowings | ✅ |
| POST | `/borrowings/` | Borrow a book | ✅ |
| GET | `/borrowings/{id}/` | Get borrowing details | ✅ |
| POST | `/borrowings/{id}/return/` | Return a book | ✅ |

**Borrowing Filters:**
```
GET /borrowings/?is_active=true          # Only active borrowings
GET /borrowings/?is_active=false         # Only completed borrowings
GET /borrowings/?user_id=2               # (Admin only) Filter by user
```

---

## 💡 Example Workflows

### 1. Register & Get Token
```bash

# Register
curl -X POST http://127.0.0.1:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "secure123",
    "first_name": "John",
    "last_name": "Doe"
  }'

# Login
curl -X POST http://127.0.0.1:8000/users/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "secure123"
  }'
```

### 2. Browse Books
```bash

# List all books
curl http://127.0.0.1:8000/books/

# Get specific book
curl http://127.0.0.1:8000/books/1/
```

### 3. Borrow a Book
```bash

curl -X POST http://127.0.0.1:8000/borrowings/ \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "book": 1,
    "expected_return_date": "2025-04-01"
  }'
```

### 4. Return a Book
```bash

curl -X POST http://127.0.0.1:8000/borrowings/1/return/ \
  -H "Authorization: Bearer your_access_token"
```

### 5. View Your Profile
```bash

curl -X GET http://127.0.0.1:8000/users/me/ \
  -H "Authorization: Bearer your_access_token"
```

---

## 🛠️ Tools & Documentation

- **API Documentation:** `http://127.0.0.1:8000/api/swagger/`
- **Admin Panel:** `http://127.0.0.1:8000/admin/`
- **Database:** SQLite (local development)

---

## 📋 Data Models

### User
- `email` - Unique email address
- `first_name` - User's first name
- `last_name` - User's last name
- `password` - Encrypted password
- `is_staff` - Admin flag

### Book
- `title` - Book title
- `author` - Author name
- `cover` - HARD or SOFT
- `inventory` - Number of copies available
- `daily_fee` - Daily rental fee in USD

### Borrowing
- `user` - User who borrowed
- `book` - Borrowed book
- `borrow_date` - Date borrowed (auto-set)
- `expected_return_date` - When book should be returned
- `actual_return_date` - When book was actually returned (null if not returned)

---

## 🔒 Permissions

- **Public:** View books, register, login
- **Authenticated Users:** Borrow books, manage profile, view own borrowings
- **Admin Users:** Create/edit/delete books, view all borrowings

---

## 🐛 Troubleshooting

### Python Version Issues
**Error: `ModuleNotFoundError` or incompatible dependencies?**
```bash

# Check your Python version (should be 3.11+)
python --version

# If you have multiple Python versions, specify explicitly
python3.11 -m venv .venv
python3.11 -m pip install -r requirements.txt
```

### 401 Unauthorized?
- Check your token is valid: 
  ```bash
  curl -X POST http://127.0.0.1:8000/users/token/refresh/ \
    -H "Content-Type: application/json" \
    -d '{"refresh":"your_refresh_token"}'
  ```
- Ensure header is set correctly: `Authorization: Bearer your_token`
- Token must include "Bearer " prefix before the token

### Book not available?
- Check inventory is > 0: 
  ```bash
  curl http://127.0.0.1:8000/books/1/
  ```
- Try to borrow only when `"inventory": 1` or higher

---

## 📝 Development

```bash

# Run tests
python manage.py test

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Access Django shell
python manage.py shell
```

---

**Happy borrowing!** 📖