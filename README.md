# Backend API

This is the backend for the project, built with FastAPI, SQLModel, and APScheduler.

## Requirements

- Python 3.11+
- Poetry

## Setup

1. Install dependencies:

```bash
poetry install
```

2. Configure environment variables:

```bash
cp .env.template .env
```

Edit `.env` to add your credentials.

## Running the Server

To start the API server (which also starts the scheduler):

```bash
poetry run uvicorn src.main:app --reload
```

The API will be available at http://localhost:8000.
Documentation is available at http://localhost:8000/docs.

## Admin Dashboard

The admin dashboard provides a web interface and REST API for managing configurations, monitoring jobs, and controlling uploads.

📚 **Documentation:**
- [Admin Guide](ADMIN_GUIDE.md) - Comprehensive administrator documentation
- [Screenshots & Usage Examples](SCREENSHOTS.md) - Visual guide with examples

### Accessing the Dashboard

**Web UI**: Navigate to http://localhost:8000/admin/dashboard

**API Documentation**: Visit http://localhost:8000/docs for interactive API documentation

### Authentication

All admin endpoints require API key authentication. Include your API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key-here" http://localhost:8000/admin/status
```

Set your API key in the `.env` file:
```
ADMIN_API_KEY=your-secure-api-key
```

### Features

#### 1. Channel Management

Manage YouTube channel configurations including content type, video style, and AI provider preferences.

**List all channels:**
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/admin/channels
```

**Create a new channel:**
```bash
curl -X POST http://localhost:8000/admin/channels \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_name": "Tech Tutorials",
    "channel_id": "UC123456789",
    "description": "Educational tech content",
    "content_type": "educational",
    "video_length": "short",
    "video_style": "informative",
    "ai_provider": "openai"
  }'
```

**Update a channel:**
```bash
curl -X PUT http://localhost:8000/admin/channels/1 \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "tutorial",
    "video_style": "professional"
  }'
```

**Delete a channel:**
```bash
curl -X DELETE http://localhost:8000/admin/channels/1 \
  -H "X-API-Key: your-api-key"
```

#### 2. Upload Schedule Management

Configure automated upload schedules for your channels.

**Create a schedule:**
```bash
curl -X POST http://localhost:8000/admin/schedules \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": 1,
    "frequency": "daily",
    "preferred_time": "09:00",
    "timezone": "UTC",
    "is_active": true
  }'
```

**List all schedules:**
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/admin/schedules
```

**Update a schedule:**
```bash
curl -X PUT http://localhost:8000/admin/schedules/1 \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "frequency": "weekly",
    "preferred_time": "14:00"
  }'
```

#### 3. Job Monitoring

View the history of background jobs and upcoming scheduled tasks.

**View job history:**
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/admin/jobs/history?limit=50
```

**View upcoming jobs:**
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/admin/jobs/upcoming
```

#### 4. Upload History

Track all video uploads and their status.

**View upload history:**
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/admin/uploads/history?limit=50
```

**Get last upload:**
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/admin/uploads/last
```

#### 5. Manual Actions

Trigger manual operations from the dashboard.

**Trigger YouTube OAuth:**
```bash
curl -X POST "http://localhost:8000/admin/actions/trigger-oauth?channel_id=1" \
  -H "X-API-Key: your-api-key"
```

Response includes the OAuth URL to visit for authorization:
```json
{
  "message": "OAuth flow initiated",
  "oauth_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
  "instructions": "Visit the oauth_url to authorize YouTube access"
}
```

**Test AI Generation:**
```bash
curl -X POST http://localhost:8000/admin/actions/test-ai-generation \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "job_name": "test_ai_generation",
    "details": "Testing OpenAI integration"
  }'
```

**Queue Manual Upload:**
```bash
curl -X POST "http://localhost:8000/admin/actions/queue-upload?channel_id=1" \
  -H "X-API-Key: your-api-key"
```

#### 6. System Status

Get an overview of the system's operational status.

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/admin/status
```

Response example:
```json
{
  "system_status": "operational",
  "scheduler_running": true,
  "total_channels": 5,
  "active_schedules": 3,
  "recent_job_count": 10,
  "failed_job_count": 1,
  "ai_providers": {
    "openai": true,
    "anthropic": false
  },
  "youtube_configured": true
}
```

### Web Interface

The web interface provides an intuitive UI for all admin operations:

- **Overview**: System status dashboard with stats and recent jobs
- **Channels**: Manage channel configurations
- **Schedules**: Configure upload timetables
- **Job History**: Monitor job execution history
- **Uploads**: Track video upload status
- **Actions**: Trigger manual operations (OAuth, AI tests, uploads)

To access the web interface:
1. Navigate to http://localhost:8000/admin/dashboard
2. Enter your API key (from the `ADMIN_API_KEY` environment variable)
3. Use the tabbed interface to navigate between different sections

### Quick Start Demo

A demo script is provided to showcase the API functionality:

```bash
# Make sure the server is running first
poetry run uvicorn src.main:app --reload &

# Run the demo script
./examples/demo_api.sh
```

This script demonstrates:
- Checking system status
- Creating channels and schedules
- Testing AI generation
- Viewing job history and upcoming jobs

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| APP_NAME | Name of the application | Backend API |
| ENV | Environment (development, production) | development |
| DATABASE_URL | Database connection string | sqlite:///./backend.db |
| ADMIN_API_KEY | API key for admin dashboard access | change-me-in-production |
| OPENAI_API_KEY | OpenAI API Key | |
| ANTHROPIC_API_KEY | Anthropic API Key | |
| YOUTUBE_API_KEY | YouTube Data API Key | |
| YOUTUBE_CLIENT_ID | YouTube OAuth Client ID | |
| YOUTUBE_CLIENT_SECRET | YouTube OAuth Client Secret | |

## Database Models

The project uses SQLModel (SQLAlchemy) for database interactions.

- **ChannelConfig**: Stores channel configuration including content type, video preferences, and AI provider
- **SchedulePreference**: Stores scheduling preferences for automated uploads
- **JobRunHistory**: Stores the history of background job executions
- **UploadHistory**: Tracks video upload attempts and their results

## Development Tools

### Linting

We use `ruff` for linting.

```bash
poetry run ruff check .
```

### Testing

We use `pytest` for testing.

```bash
poetry run pytest
```

## Security Considerations

- **Change the default API key**: Always set a strong `ADMIN_API_KEY` in production
- **Use HTTPS**: In production, ensure all admin endpoints are served over HTTPS
- **Protect your .env file**: Never commit `.env` files to version control
- **Rotate credentials**: Regularly rotate API keys and OAuth tokens
