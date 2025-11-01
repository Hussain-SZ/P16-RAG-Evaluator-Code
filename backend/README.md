# RAG Evaluator Backend

A FastAPI-based backend service for the RAG (Retrieval-Augmented Generation) Evaluator application.

## Project Structure

```
backend/
├── app/
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── api.py          # Main API router
│   │   ├── auth.py         # Authentication endpoints
│   │   └── protected.py    # Protected endpoints
│   ├── config/             # Configuration
│   │   ├── __init__.py
│   │   └── settings.py     # Application settings
│   ├── core/               # Core functionality
│   │   ├── __init__.py
│   │   └── security.py     # Authentication & JWT handling
│   ├── database/           # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py   # MongoDB connection
│   │   └── repositories.py # Database operations
│   ├── models/             # Pydantic models
│   │   ├── __init__.py
│   │   └── user.py         # User model
│   ├── schemas/            # Request/Response schemas
│   │   ├── __init__.py
│   │   └── auth.py         # Authentication schemas
│   ├── services/           # Business logic
│   │   ├── __init__.py
│   │   └── auth_service.py # Authentication service
│   ├── utils/              # Utilities
│   │   ├── __init__.py
│   │   └── helpers.py      # Helper functions
│   └── main.py             # FastAPI application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Features

- **Authentication System**: Complete user registration, login, and JWT-based authentication
- **Email Verification**: OTP-based email verification using SendGrid
- **Password Reset**: Secure password reset with OTP verification
- **MongoDB Integration**: Full MongoDB integration with proper connection handling
- **Clean Architecture**: Organized into layers (API, Services, Repository, Models)
- **Configuration Management**: Environment-based configuration with Pydantic Settings
- **Error Handling**: Comprehensive error handling with proper HTTP status codes
- **CORS Support**: Configurable CORS for frontend integration
- **Logging**: Structured logging throughout the application

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Setup

Copy the environment template and configure your variables:

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```env
MONGO_URI=mongodb://localhost:27017
JWT_SECRET=your-super-secret-jwt-key-here-make-it-long-and-random
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
```

### 3. Run the Application

From the project root directory:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication (`/api/v1/auth`)

- `POST /register` - Register new user (sends OTP)
- `POST /verify-otp` - Verify OTP and complete registration
- `POST /resend-otp` - Resend OTP for verification
- `POST /login` - User login
- `POST /forgot-password` - Request password reset OTP
- `POST /reset-password` - Reset password with OTP

### Protected Routes (`/api/v1/protected`)

- `GET /me` - Get current user info (requires authentication)
- `GET /dashboard` - Protected dashboard endpoint

### General

- `GET /` - Root endpoint with API info
- `GET /health` - Health check endpoint

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MONGO_URI` | Yes | - | MongoDB connection string |
| `JWT_SECRET` | Yes | - | Secret key for JWT tokens |
| `SENDGRID_API_KEY` | No | - | SendGrid API key for email |
| `SENDGRID_FROM_EMAIL` | No | noreply@ragevaluator.com | From email address |
| `DEBUG` | No | false | Debug mode |

## Development

### Code Organization

- **API Layer** (`api/`): FastAPI routes and request handling
- **Service Layer** (`services/`): Business logic and orchestration
- **Repository Layer** (`database/repositories.py`): Data access operations
- **Model Layer** (`models/`): Database models (MongoDB documents)
- **Schema Layer** (`schemas/`): Request/response validation schemas
- **Core Layer** (`core/`): Authentication, security, and core utilities

### Database

The application uses MongoDB with the following collections:

- **users**: User accounts and authentication data

### Authentication Flow

1. **Registration**: User provides name, email, password → OTP sent to email
2. **Verification**: User enters OTP → Account created and JWT returned
3. **Login**: User provides email/password → JWT returned
4. **Password Reset**: User requests reset → OTP sent → New password set with OTP

### Security Features

- Password hashing with bcrypt
- JWT tokens with configurable expiration
- OTP-based verification (10-minute expiry)
- Protected routes with token validation
- Input validation with Pydantic

## Production Deployment

For production deployment, consider:

1. **Environment Variables**: Set all required environment variables
2. **Database**: Use MongoDB Atlas or a production MongoDB instance
3. **Email Service**: Configure SendGrid for email notifications
4. **Security**: Use strong JWT secrets and proper CORS configuration
5. **Logging**: Configure proper logging levels and destinations
6. **Monitoring**: Add health checks and monitoring

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Contributing

1. Follow the existing code structure and patterns
2. Add proper error handling and logging
3. Include type hints for all functions
4. Update this README when adding new features
5. Test endpoints using the interactive docs at `/docs`