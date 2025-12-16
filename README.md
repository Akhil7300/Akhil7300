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

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| APP_NAME | Name of the application | Backend API |
| ENV | Environment (development, production) | development |
| DATABASE_URL | Database connection string | sqlite:///./backend.db |
| OPENAI_API_KEY | OpenAI API Key | |
| ANTHROPIC_API_KEY | Anthropic API Key | |
| YOUTUBE_API_KEY | YouTube Data API Key | |

## Database Models

The project uses SQLModel (SQLAlchemy) for database interactions.

- **ChannelConfig**: Stores channel configuration.
- **ContentConfig**: Stores content generation configuration for channels.
- **SchedulePreference**: Stores scheduling preferences for channels (frequency, timezone, etc.).
- **JobRunHistory**: Stores the history of background jobs with status, video URLs, and error messages.

## Automation Workflow

The system implements a comprehensive automation workflow for scheduled video uploads:

### Components

1. **Coordinator Service** (`src/services/coordinator.py`)
   - Orchestrates the entire upload workflow
   - Reads channel and content configuration from database
   - Invokes AI generation pipeline
   - Uploads via YouTube client
   - Logs all operations with structured logging
   - Records job outcomes in database

2. **APScheduler Integration** (`src/services/scheduler.py`, `src/services/scheduler_manager.py`)
   - Registers per-channel jobs with user-selected cadence and timezones
   - Persists job state in database (SQLAlchemy job store)
   - Automatically syncs jobs from database on startup
   - Calculates and tracks next run times

3. **AI Generation** (`src/services/ai_generator.py`)
   - Generates video content (title, description, script, tags)
   - Supports multiple AI models (OpenAI, Anthropic)
   - Falls back to placeholder content if no API key provided

4. **YouTube Client** (`src/services/youtube_client.py`)
   - Handles video uploads to YouTube
   - Returns video URL on success
   - Falls back to mock uploads if no API key provided

5. **Alert Service** (`src/services/alert_service.py`)
   - Sends success/failure alerts
   - Placeholder implementations for email and webhook alerts
   - Extensible for production integrations

### API Endpoints

- `POST /coordinator/trigger` - Manually trigger an upload for a specific channel
- `GET /coordinator/jobs/history` - Get job execution history (filterable by channel)
- `POST /coordinator/jobs/register/{channel_id}` - Register a scheduled job
- `DELETE /coordinator/jobs/unregister/{channel_id}` - Unregister a scheduled job

### Job Status Tracking

Each job execution is tracked with:
- Start and end times
- Status (running, success, failure)
- Video URL (on success)
- Error message (on failure)
- Additional details

### Logging

The system uses structured JSON logging for comprehensive observability:
- All operations are logged with context
- Errors include stack traces
- Request/response timing tracked via middleware

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
