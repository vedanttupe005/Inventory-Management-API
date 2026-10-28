# Inventory Management API

A RESTful Inventory Management System built with **Flask, PostgreSQL, and SQLAlchemy**. The API provides secure authentication, role-based access control, product and category management, inventory tracking, order management, pagination, filtering, Redis caching, and rate limiting.

The project follows a modular backend architecture and uses Docker to simplify development and deployment.

## Features

### Authentication and Authorization
- User registration and login.
- JWT access tokens and refresh tokens.
- Token revocation using a JWT blocklist.
- Secure password hashing with Werkzeug.
- Role-based access control using custom decorators.
- Roles: Admin, Manager, Staff, and User.
- Rate limiting on authentication endpoints.

### Product Management
- Create, retrieve, update, and delete products.
- Search products by name.
- Filter products by category, price, and quantity.
- Paginated product listings with configurable page size.
- Category-based product organization.
- Redis caching for product listing endpoints.

### Category Management
- Create, retrieve, update, and delete categories.
- Associate multiple products with a category.
- Prevent category deletion when associated products exist.
- Cache invalidation when category data changes.

### Inventory Tracking
- Update product stock quantities.
- Retrieve low-stock products.
- Maintain inventory history logs for stock-related changes.
- Record inventory changes associated with supported product and order operations.

### Order Management
- Associate orders with users.
- Support multiple products in an order through relational database associations.
- Track order status, including Pending, Processing, Completed, and Cancelled.
- Restore stock and record inventory changes when an order is cancelled.

### Performance and Reliability
- PostgreSQL relational database.
- SQLAlchemy ORM and Flask-Migrate database migrations.
- Redis caching using Flask-Caching.
- Flask-Limiter rate limiting.
- Marshmallow request validation.
- Structured JSON error responses.
- Pytest automated tests.
- Docker and Docker Compose support.
- Swagger/OpenAPI API documentation.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| Flask | REST API framework |
| PostgreSQL | Relational database |
| SQLAlchemy | ORM and database queries |
| Flask-Migrate | Database migrations |
| Flask-JWT-Extended | JWT authentication |
| Marshmallow | Data validation and serialization |
| Redis | Caching backend |
| Flask-Caching | Application caching |
| Flask-Limiter | Rate limiting |
| Pytest | Automated testing |
| Swagger / OpenAPI | API documentation |
| Docker | Containerization |
| Docker Compose | Multi-container development |

## Project Structure

```text
Inventory-Management-API/
│
├── app/
│   ├── auth/
│   ├── products/
│   ├── categories/
│   ├── inventory/
│   ├── orders/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   ├── extensions.py
│   └── config.py
│
├── migrations/
├── tests/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── run.py
├── .env.example
├── .gitignore
└── README.md
```

*The directory listing is illustrative; retain the actual module and file names in your repository.*

## Getting Started

### Prerequisites

For local development, install:

- Python 3.11 or later, compatible with your project dependencies.
- PostgreSQL.
- Redis.
- Git.

Alternatively, use Docker Desktop with Docker Compose to run the containerized application and its configured services.

### 1. Clone the repository

```bash
git clone https://github.com/vedanttupe005/Inventory-Management-API.git
cd Inventory-Management-API
```

Replace the placeholders with your repository URL and directory name.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On Linux or macOS:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root. Use the variable names expected by your application's configuration.

Example:

```dotenv
# Database configuration
DATABASE_URL=postgresql://postgres:postgres@db:5432/inventory
TEST_DATABASE_URL=postgresql://postgres:admin@localhost:5433/inventory_test_db

# Redis configuration
RATELIMIT_STORAGE_URI=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379

# Flask configuration
FLASK_APP=run.py
FLASK_ENV=development

# Security — replace with secure values
SECRET_KEY=replace_with_a_secure_secret
JWT_SECRET_KEY=replace_with_a_secure_jwt_secret
```

**Important:** These are example variable names. If your `Config` class uses `SQLALCHEMY_DATABASE_URI`, separate Redis host and port variables, or other names, update the example to match the actual configuration. Never commit real secrets or database credentials to GitHub.

### 5. Run database migrations

Ensure PostgreSQL is running and the configured database exists.

Apply migrations:

```bash
flask db upgrade
```

If your Flask application requires an explicit application entry point, configure `FLASK_APP` as appropriate for your project before running the command.

### 6. Start the application

```bash
python run.py
```

The API will typically be available at:

```text
http://127.0.0.1:5000
```

The development server is intended for local development, not production deployment.

## Running with Docker

Docker Compose is the recommended way to run the application with its supporting services.

Build the images and start the containers:

```bash
docker compose up --build
```

Run the database migrations inside the API container:

```bash
docker compose exec api flask db upgrade
```

Check the running containers:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f api
```

Stop the services:

```bash
docker compose down
```

Your Docker Compose configuration should supply the database connection string, JWT secrets, and Redis connection settings to the API container. Within the Compose network, use the appropriate service names for PostgreSQL and Redis rather than `localhost`.

## API Documentation

The API uses Swagger/OpenAPI documentation to describe endpoints, request parameters, authentication requirements, and responses.

When the application is running, open the configured Swagger UI route. For example, if Swagger UI is configured at `/swagger-ui`:

```text
http://127.0.0.1:5000/swagger-ui
```

The exact URL depends on the application's OpenAPI configuration.

For protected endpoints, obtain a JWT access token through the login endpoint and authorize requests using the Bearer token mechanism supported by the API documentation.

## API Endpoints

The following table summarizes the principal API operations. Actual URL prefixes and supported methods depend on the registered Flask blueprints.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register a user |
| POST | `/api/v1/auth/login` | Authenticate a user |
| POST | `/api/v1/auth/refresh` | Obtain a new access token |
| POST | `/api/v1/auth/logout` | Revoke a token according to the configured token policy |

### Products

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/products` | Create a product |
| GET | `/api/v1/products` | List products |
| GET | `/api/v1/products/<id>` | Retrieve a product |
| PATCH | `/api/v1/products/<id>` | Partially update a product |
| PUT | `/api/v1/products/<id>` | Replace a product, if supported |
| DELETE | `/api/v1/products/<id>` | Delete a product |

### Categories

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/categories` | Create a category |
| GET | `/api/v1/categories` | List categories |
| GET | `/api/v1/categories/<id>` | Retrieve a category |
| PATCH | `/api/v1/categories/<id>` | Update a category |
| DELETE | `/api/v1/categories/<id>` | Delete a category when permitted |

### Inventory

| Method | Endpoint | Description |
|---|---|---|
| PATCH | `/api/v1/inventory/<id>` | Update inventory, according to the configured route |
| GET | `/api/v1/inventory/low-stock` | Retrieve low-stock products |
| GET | `/api/v1/inventory/logs/low-stock` | Retrieve low-stock-related inventory logs, if registered at this path |

### Orders

Order creation, retrieval, status updates, and cancellation should use the routes registered by the order blueprint. Consult Swagger UI for the exact endpoint paths and request schemas.

**Note:** The paths above are documentation examples based on the intended API design. Verify them against your registered routes before publishing the README.

## Pagination, Search, and Filtering

The product listing endpoint supports pagination and query-based filtering.

Example request:

```http
GET /api/v1/products?page=1&limit=10
```

Search by product name:

```http
GET /api/v1/products?search=laptop
```

Filter by category:

```http
GET /api/v1/products?category=electronics
```

Filter by price:

```http
GET /api/v1/products?price_lt=50000
```

Filter by quantity:

```http
GET /api/v1/products?quantity_gt=5
```

Multiple filters can be combined when supported by the route implementation.

The paginated response should communicate the current page, total pages, and total record count, along with the returned records.

## Authentication Example

Register a user using the configured registration schema:

```http
POST /api/v1/auth/register
Content-Type: application/json
```

Example request body:

```json
{
  "username": "demo_user",
  "email": "demo@example.com",
  "password": "ChangeMe123!"
}
```

The request fields must match the actual Marshmallow schema.

Log in to obtain a JWT token:

```http
POST /api/v1/auth/login
Content-Type: application/json
```

Example request body:

```json
{
  "email": "demo@example.com",
  "password": "ChangeMe123!"
}
```

Use the returned access token for protected requests:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

Use a locally created demo account for testing. Never publish real credentials or access tokens.

## Role-Based Access Control

The API uses role-based authorization to restrict sensitive operations.

| Role | Intended permissions |
|---|---|
| Admin | Administrative operations, including product deletion |
| Manager | Inventory updates and permitted management operations |
| Staff | Read-only inventory access |
| User | Access according to the permissions configured for the account |

Role checks are implemented using a custom decorator, such as:

```python
@role_required("admin")
```

The actual permissions depend on the decorators applied to each route.

## Caching and Rate Limiting

### Redis Caching

Redis is used as the caching backend through Flask-Caching.

The implementation includes caching for selected listing endpoints and cache invalidation for relevant category mutations. Product listing caching can also account for query-string parameters when configured accordingly.

Caching reduces repeated database work, while invalidation helps prevent stale responses after updates.

### Rate Limiting

Flask-Limiter protects selected endpoints against excessive requests. Authentication endpoints are particularly important because they can be targeted by automated abuse.

Rate limits should be configured through the application's settings and adjusted for production traffic.

## Database Design

The database uses SQLAlchemy models and relational associations.

Core entities include:

- **User:** Account information, hashed password, and role.
- **Category:** Product classification.
- **Product:** Product details, pricing, quantity, and category association.
- **Order:** Order owner, status, total amount, and timestamps.
- **InventoryLog:** Records supported inventory changes.
- **Order–Product association:** Represents the relationship between orders and products.

Database schema changes are managed with Flask-Migrate and Alembic.

## Validation and Error Handling

Marshmallow schemas validate incoming data and serialize responses where configured.

The API should reject invalid input, including negative prices, negative quantities, malformed email addresses, and missing required fields.

Errors are returned as JSON with appropriate HTTP status codes.

Common status codes include:

| Status | Meaning |
|---|---|
| 200 | Request completed successfully |
| 201 | Resource created |
| 400 | Invalid request |
| 401 | Authentication required or invalid |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 429 | Rate limit exceeded |
| 500 | Unexpected server error |

Example error response:

```json
{
  "error": "Product not found"
}
```

## Testing

The project uses Pytest to verify API behavior.

Run the test suite:

```bash
python -m pytest
```

Run tests with code coverage:

```bash
python -m pytest --cov=app --cov-report=term-missing
```

The coverage report helps identify which application modules and lines are exercised by the tests.

Ensure that tests use a separate test database and that testing configuration disables or adjusts rate limiting when appropriate. Never run destructive test setup against a production database.

## Security Practices

- Hash passwords instead of storing plaintext passwords.
- Keep secret keys and credentials in environment variables.
- Use JWT authentication for protected endpoints.
- Apply role checks to sensitive operations.
- Validate user input before database changes.
- Configure rate limits for sensitive endpoints.
- Keep production debug mode disabled.
- Use HTTPS in production.
- Restrict database access and use appropriate database permissions.
- Never commit `.env`, access tokens, or private credentials to source control.

## Deployment

The application is containerized and can be deployed to a suitable hosting platform or VPS.

A production deployment should include:

1. A production WSGI server such as Gunicorn.
2. PostgreSQL with persistent storage and backups.
3. Redis for configured caching and rate limiting.
4. Environment-specific configuration and secure secrets.
5. Database migrations during controlled deployment.
6. HTTPS termination through a reverse proxy such as Nginx or a managed hosting service.
7. Logging, health checks, and monitoring.

A successful local Docker build does not, by itself, mean that the application is deployed publicly. Add your verified live API URL here once deployment is complete.

**Live API:** Add your deployed URL.

**Swagger Documentation:** Add your deployed Swagger UI URL.

## Future Improvements

Potential extensions include:

- Product image upload with secure file storage.
- More comprehensive order lifecycle validation.
- Integration and authorization test coverage across every module.
- CI/CD with automated tests and image builds.
- Redis-backed caching improvements and cache invalidation tests.
- Production health checks and structured logging.
- Deployment monitoring and automated database backups.

## Learning Outcomes

This project demonstrates practical experience with:

- REST API development using Flask.
- Relational database design and ORM usage.
- JWT authentication and role-based authorization.
- Request validation and structured error handling.
- Pagination, searching, and filtering.
- Caching and rate limiting.
- Automated API testing.
- Docker-based development and deployment preparation.
- API documentation using OpenAPI/Swagger.

## License

Add a license appropriate for your repository, such as the MIT License, if you intend to distribute the project under those terms.

---

**Built with Python, Flask, PostgreSQL, SQLAlchemy, Redis, Pytest, and Docker.**
