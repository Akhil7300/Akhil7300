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
- **SchedulePreference**: Stores scheduling preferences for channels.
- **JobRunHistory**: Stores the history of background jobs.

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
