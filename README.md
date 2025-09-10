# Multi-Service Automation Platform - Mid-Level

A **production-ready, enterprise-grade** FastAPI-based platform that unifies communication across Slack, Telegram, and Google Sheets with advanced features including RBAC, rate limiting, caching, monitoring, and comprehensive admin capabilities.

## 🚀 **Mid-Level Features**

### **🔐 Advanced Authentication & Authorization**
- **JWT-based Authentication** with refresh tokens
- **Role-Based Access Control (RBAC)** with granular permissions
- **User Session Management** with device tracking
- **Multi-factor Authentication** support
- **API Key Management** for service integrations

### **⚡ Performance & Scalability**
- **Redis Caching** with intelligent cache invalidation
- **Rate Limiting** with sliding window algorithm
- **Background Job Processing** with Celery
- **Database Connection Pooling** and optimization
- **Async/Await** throughout the application

### **📊 Monitoring & Observability**
- **Real-time Metrics** collection and aggregation
- **Health Checks** for all services and dependencies
- **API Analytics** with usage tracking and reporting
- **Performance Monitoring** with response time tracking
- **Error Tracking** with detailed logging and alerting

### **🛡️ Security & Compliance**
- **Input Validation** with Pydantic schemas
- **SQL Injection Protection** with SQLAlchemy ORM
- **XSS Protection** with proper output encoding
- **CSRF Protection** with token validation
- **Audit Logging** for all admin actions

### **🔧 Admin & Management**
- **Admin Dashboard** with comprehensive user management
- **Role & Permission Management** with granular controls
- **System Monitoring** with real-time statistics
- **Cache Management** with Redis insights
- **API Usage Analytics** with detailed reporting

### **🌐 API Features**
- **API Versioning** with deprecation handling
- **Comprehensive Documentation** with Swagger/OpenAPI
- **Request/Response Validation** with detailed error messages
- **WebSocket Support** for real-time updates
- **Webhook Security** with signature validation

## 🏗️ **Architecture**

```
e_agent/
├── app/                          # FastAPI application
│   ├── api/v1/                   # API routes
│   │   ├── auth.py              # JWT authentication & RBAC
│   │   ├── messages.py          # Unified messaging endpoints
│   │   ├── sheets.py            # Google Sheets integration
│   │   ├── websocket.py         # Real-time WebSocket support
│   │   └── admin.py             # Admin panel & management
│   ├── core/                    # Core configuration
│   │   ├── config.py            # Pydantic settings
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── security.py          # JWT & password hashing
│   │   ├── celery.py            # Background job configuration
│   │   ├── rate_limiting.py     # Rate limiting utilities
│   │   ├── cache.py             # Redis caching utilities
│   │   ├── monitoring.py        # Metrics & health checks
│   │   ├── exceptions.py        # Custom exception handling
│   │   └── versioning.py        # API versioning
│   ├── models/                  # Database models
│   │   ├── user.py              # User model with RBAC
│   │   └── role.py              # Role & permission models
│   ├── schemas/                 # Pydantic schemas
│   │   ├── user.py              # User request/response schemas
│   │   ├── message.py           # Message schemas
│   │   └── admin.py             # Admin panel schemas
│   ├── main.py                  # FastAPI app entry point
│   └── tasks.py                 # Celery background tasks
├── services/                    # External service integrations
│   ├── slack_service.py         # Slack API integration
│   ├── telegram_service.py      # Telegram Bot API integration
│   └── sheets_service.py        # Google Sheets API integration
├── tests/                       # Comprehensive test suite
├── docker-compose.yml           # Multi-service orchestration
├── Dockerfile                   # Application containerization
├── pyproject.toml               # Modern Python project config
└── README.md                    # This file
```

## 🛠️ **Tech Stack**

- **Backend**: FastAPI, SQLAlchemy, Alembic
- **Database**: PostgreSQL with connection pooling
- **Cache**: Redis with intelligent caching strategies
- **Authentication**: JWT with RBAC and session management
- **Background Jobs**: Celery with Redis broker
- **Messaging**: Slack SDK, python-telegram-bot
- **Sheets**: Google API Client with OAuth2
- **Monitoring**: Custom metrics, health checks, analytics
- **Containerization**: Docker, docker-compose
- **Testing**: pytest with comprehensive coverage

## 📋 **Prerequisites**

- Python 3.11+
- Docker and docker-compose
- PostgreSQL 15+
- Redis 7+
- Google Cloud Project with Sheets API enabled
- Slack App with Bot Token
- Telegram Bot Token

## 🚀 **Quick Start**

### 1. Clone and Setup

```bash
git clone <repository-url>
cd e_agent
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file with your credentials:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/automation_platform

# JWT
SECRET_KEY=your-super-secret-key-change-this-in-production

# Redis
REDIS_URL=redis://localhost:6379/0

# Slack
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_SIGNING_SECRET=your-slack-signing-secret

# Telegram
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/v1/telegram/webhook

# Google Sheets
GOOGLE_CREDENTIALS_FILE=credentials.json
```

### 3. Run with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### 4. Run Locally (Development)

```bash
# Install dependencies
pip install -e .

# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Run migrations
alembic upgrade head

# Start the application
uvicorn app.main:app --reload

# Start Celery worker (in another terminal)
celery -A app.core.celery worker --loglevel=info
```

## 📚 **API Documentation**

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **Key Endpoints**

#### **Authentication & Authorization**
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/refresh` - Refresh JWT token

#### **Messaging**
- `POST /api/v1/messages/send` - Send unified message to multiple services
- `POST /api/v1/messages/slack` - Send Slack message only
- `POST /api/v1/messages/telegram` - Send Telegram message only

#### **Google Sheets**
- `POST /api/v1/sheets/append` - Append row to sheet
- `POST /api/v1/sheets/read` - Read data from sheet
- `POST /api/v1/sheets/update` - Update sheet data

#### **Admin Panel**
- `GET /api/v1/admin/stats/overview` - System overview statistics
- `GET /api/v1/admin/users` - List users with pagination
- `GET /api/v1/admin/api/stats` - API usage statistics
- `GET /api/v1/admin/cache/stats` - Cache statistics

#### **Monitoring**
- `GET /health` - Comprehensive health check
- `GET /metrics` - Application metrics
- `GET /api/v1/ws/connect` - WebSocket for real-time updates

## 🔧 **Advanced Usage Examples**

### **Send Unified Message with Rate Limiting**

```bash
curl -X POST "http://localhost:8000/api/v1/messages/send" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "API-Version: v2" \
  -d '{
    "content": "Hello from the automation platform!",
    "services": ["slack", "telegram"],
    "slack_channel": "C1234567890",
    "telegram_chat_id": "456789"
  }'
```

### **Admin Operations**

```bash
# Get system overview
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  "http://localhost:8000/api/v1/admin/stats/overview"

# List users with pagination
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  "http://localhost:8000/api/v1/admin/users?page=1&size=20"

# Get API statistics
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  "http://localhost:8000/api/v1/admin/api/stats?hours=24"
```

## 🧪 **Testing**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov=services

# Run specific test file
pytest tests/test_admin.py

# Run with verbose output
pytest -v
```

## 📊 **Monitoring & Metrics**

### **Health Checks**
- Database connectivity and performance
- Redis cache status and performance
- External service availability
- System resource usage

### **Metrics Collected**
- Request/response times
- API usage statistics
- Error rates and types
- Cache hit/miss ratios
- Background job performance

### **Admin Dashboard Features**
- User management and role assignment
- System performance monitoring
- API usage analytics
- Cache performance insights
- Real-time system statistics

## 🔄 **Background Jobs**

The platform uses Celery for background job processing:

- **Health Checks**: Periodic system health monitoring
- **Async Messaging**: Non-blocking message sending
- **Webhook Processing**: Asynchronous webhook data processing
- **Sheet Operations**: Background Google Sheets operations
- **Cache Management**: Automatic cache cleanup and optimization

## 🌐 **WebSocket Support**

Real-time updates are available via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/connect?token=YOUR_JWT_TOKEN');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Real-time update:', data);
};
```

## 🚀 **Production Deployment**

### **Environment Variables**

```env
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:pass@prod-db:5432/automation_platform
REDIS_URL=redis://prod-redis:6379/0
```

### **Security Considerations**

- Use strong, unique SECRET_KEY
- Enable HTTPS in production
- Configure proper CORS origins
- Use environment-specific database credentials
- Rotate API keys regularly
- Enable audit logging

### **Scaling**

- Use multiple Celery workers
- Implement Redis clustering for high availability
- Use PostgreSQL read replicas
- Consider load balancing for the FastAPI app
- Implement horizontal pod autoscaling

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 **Support**

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the test files for usage examples

## 🔮 **Roadmap**

- [ ] React admin dashboard
- [ ] Advanced message templating
- [ ] Message scheduling and automation
- [ ] Analytics and reporting dashboard
- [ ] Multi-tenant support
- [ ] Advanced webhook filtering
- [ ] Message encryption support
- [ ] GraphQL API support
- [ ] Mobile app integration
- [ ] Advanced monitoring with Grafana

---

**This is a mid-level portfolio project demonstrating enterprise-grade development skills with production-ready features!** 🎉
