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
| YOUTUBE_API_KEY | YouTube Data API key (not used for uploads) | |
| YOUTUBE_OAUTH_CLIENT_SECRETS_FILE | Path to Google OAuth client secrets JSON | |
| YOUTUBE_OAUTH_CLIENT_SECRETS_JSON | Google OAuth client secrets JSON payload | |
| YOUTUBE_OAUTH_REDIRECT_URI | OAuth callback URL (must match Google Console) | http://localhost:8000/youtube/callback |
| YOUTUBE_TOKEN_ENCRYPTION_KEY | Fernet key used to encrypt refresh tokens in DB | |
| YOUTUBE_OAUTH_STATE_SECRET | Optional HMAC secret to sign OAuth state | |

## YouTube integration

### 1) Create Google Cloud credentials

1. Create a Google Cloud project.
2. Enable **YouTube Data API v3**.
3. Configure the OAuth consent screen.
4. Create an **OAuth Client ID** (type: **Web application**).
5. Add an authorized redirect URI:

- `http://localhost:8000/youtube/callback`

6. Download the client secrets JSON.

Set either:

- `YOUTUBE_OAUTH_CLIENT_SECRETS_FILE=/absolute/path/to/client_secret.json`, or
- `YOUTUBE_OAUTH_CLIENT_SECRETS_JSON={...}` (the full JSON contents)

### 2) Configure token encryption

Refresh tokens are stored encrypted in the database.

Generate a Fernet key and set it in `.env`:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Set the result as:

- `YOUTUBE_TOKEN_ENCRYPTION_KEY=...`

### 3) Run the connection flow

1. Start the server.
2. Generate the auth URL:

```bash
curl "http://localhost:8000/youtube/auth-url"
```

3. Open `authorization_url` in your browser.
4. After you approve access, Google will redirect to `/youtube/callback` and the backend will store the refresh token.

Verify connection status:

```bash
curl "http://localhost:8000/youtube/status"
```

### CLI status check

You can also verify connection status via CLI:

```bash
poetry run python -m src.cli youtube status
```

## Database Models

The project uses SQLModel (SQLAlchemy) for database interactions.

- **ChannelConfig**: Stores channel configuration.
- **SchedulePreference**: Stores scheduling preferences for channels.
- **JobRunHistory**: Stores the history of background jobs.
- **YouTubeOAuthToken**: Stores the encrypted YouTube refresh token.

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
