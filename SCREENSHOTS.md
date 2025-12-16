# Admin Dashboard Screenshots & Usage Guide

This document provides visual examples and detailed usage instructions for the Admin Dashboard.

## Authentication

When you first access the admin dashboard at http://localhost:8000/admin/dashboard, you'll see a login screen:

```
┌──────────────────────────────────────┐
│   Admin Dashboard Login              │
│                                      │
│   API Key:                           │
│   [________________________]         │
│                                      │
│   [Login]                            │
└──────────────────────────────────────┘
```

Enter your API key (configured via `ADMIN_API_KEY` environment variable) to access the dashboard.

## Dashboard Overview

After logging in, you'll see the main dashboard with multiple tabs:

```
┌────────────────────────────────────────────────────────────────────┐
│  Admin Dashboard                                                    │
│  Manage configurations, monitor jobs, and control uploads           │
└────────────────────────────────────────────────────────────────────┘

[Overview] [Channels] [Schedules] [Job History] [Uploads] [Actions]

┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Total    │ │ Active   │ │ Recent   │ │ Failed   │
│ Channels │ │ Schedules│ │ Jobs     │ │ Jobs     │
│    5     │ │    3     │ │   10     │ │    1     │
└──────────┘ └──────────┘ └──────────┘ └──────────┘

Recent Jobs
┌──────────────────────────────────────────────────────────────┐
│ Job Name              Type      Status    Start Time          │
├──────────────────────────────────────────────────────────────┤
│ upload_channel_1      scheduled success   2024-01-15 09:00   │
│ generate_content_2    scheduled success   2024-01-15 08:30   │
│ test_ai_generation    manual    success   2024-01-15 08:00   │
└──────────────────────────────────────────────────────────────┘
```

## Channels Tab

Manage your YouTube channels and their configurations:

```
Channel Configuration
[Create New Channel]

┌──────────────────────────────────────────────────────────────────────────┐
│ Channel Name  Content Type  Video Length  AI Provider  YouTube Connected │
├──────────────────────────────────────────────────────────────────────────┤
│ Tech Tuts     educational    short         openai       ✓ Yes            │
│ Fun Vlogs     entertainment  medium        anthropic    ✗ No             │
└──────────────────────────────────────────────────────────────────────────┘
```

**Creating a Channel:**

When you click "Create New Channel", a modal appears with these fields:
- Channel Name (required)
- Channel ID (required)
- Description
- Content Type (dropdown: educational, entertainment, tutorial, review)
- Video Length (dropdown: short, medium, long)
- Video Style (dropdown: informative, casual, professional, humorous)
- AI Provider (dropdown: openai, anthropic)

## Schedules Tab

Configure automated upload schedules:

```
Upload Schedules
[Create New Schedule]

┌───────────────────────────────────────────────────────────────────┐
│ Channel ID  Frequency  Preferred Time  Timezone  Active           │
├───────────────────────────────────────────────────────────────────┤
│ 1           daily      09:00          UTC       ✓ Yes            │
│ 2           weekly     14:00          EST       ✓ Yes            │
│ 3           monthly    10:00          UTC       ✗ No             │
└───────────────────────────────────────────────────────────────────┘
```

**Creating a Schedule:**

Schedule form includes:
- Channel ID (required)
- Frequency (daily/weekly/monthly)
- Preferred Time (HH:MM format)
- Timezone
- Active (checkbox)

## Job History Tab

Monitor background job execution:

```
Job Run History
[Refresh]

┌──────────────────────────────────────────────────────────────────────┐
│ Job Name           Type      Status   Start Time         End Time     │
├──────────────────────────────────────────────────────────────────────┤
│ upload_video_1     scheduled success  2024-01-15 09:00  09:05        │
│ generate_script_2  scheduled success  2024-01-15 08:30  08:35        │
│ test_ai_gen        manual    success  2024-01-15 08:00  08:01        │
│ upload_video_3     scheduled failure  2024-01-15 07:00  07:02        │
└──────────────────────────────────────────────────────────────────────┘

Upcoming Scheduled Jobs
┌─────────────────────────────────────────────────────────────┐
│ Job Name              Next Run Time       Trigger            │
├─────────────────────────────────────────────────────────────┤
│ daily_upload_chan_1   2024-01-16 09:00   cron[0 9 * * *]   │
│ weekly_upload_chan_2  2024-01-21 14:00   cron[0 14 * * 1]  │
└─────────────────────────────────────────────────────────────┘
```

## Uploads Tab

Track video upload history:

```
Upload History
[Refresh]

┌──────────────────────────────────────────────────────────────────┐
│ Channel ID  Video Title           Video ID     Status  Uploaded  │
├──────────────────────────────────────────────────────────────────┤
│ 1           How to Code in Python xyz123      success 2024-01-15 │
│ 2           Fun Day Vlog          abc456      success 2024-01-14 │
│ 3           Tutorial Episode 5    N/A         failure 2024-01-14 │
└──────────────────────────────────────────────────────────────────┘
```

## Actions Tab

Trigger manual operations:

```
Manual Actions

Trigger YouTube OAuth
┌────────────────────────────────────────┐
│ Channel ID: [____] [Trigger OAuth]     │
└────────────────────────────────────────┘

Test AI Generation
┌────────────────────────────────────────┐
│ Details:                                │
│ [____________________________]          │
│                                         │
│ [Test AI Generation]                   │
└────────────────────────────────────────┘

Queue Manual Upload
┌────────────────────────────────────────┐
│ Channel ID: [____] [Queue Upload]      │
└────────────────────────────────────────┘
```

## API Examples

### Example Workflow 1: Setting Up a New Channel

```bash
# 1. Create a channel
curl -X POST http://localhost:8000/admin/channels \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_name": "Tech Tutorials",
    "channel_id": "UC123456789",
    "content_type": "educational",
    "video_length": "short",
    "video_style": "informative",
    "ai_provider": "openai"
  }'

# Response:
# {
#   "id": 1,
#   "channel_name": "Tech Tutorials",
#   "channel_id": "UC123456789",
#   "content_type": "educational",
#   "video_length": "short",
#   "video_style": "informative",
#   "ai_provider": "openai",
#   "youtube_connected": false,
#   "created_at": "2024-01-15T10:00:00",
#   "updated_at": "2024-01-15T10:00:00"
# }

# 2. Create a schedule for the channel
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

# 3. Trigger YouTube OAuth
curl -X POST "http://localhost:8000/admin/actions/trigger-oauth?channel_id=1" \
  -H "X-API-Key: your-api-key"

# Response:
# {
#   "message": "OAuth flow initiated",
#   "oauth_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
#   "instructions": "Visit the oauth_url to authorize YouTube access"
# }
```

### Example Workflow 2: Monitoring System Status

```bash
# Check system status
curl -H "X-API-Key: your-api-key" http://localhost:8000/admin/status

# Response:
# {
#   "system_status": "operational",
#   "scheduler_running": true,
#   "total_channels": 5,
#   "active_schedules": 3,
#   "recent_job_count": 10,
#   "failed_job_count": 1,
#   "ai_providers": {
#     "openai": true,
#     "anthropic": false
#   },
#   "youtube_configured": true
# }

# View recent job history
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8000/admin/jobs/history?limit=10"

# View upcoming scheduled jobs
curl -H "X-API-Key: your-api-key" \
  http://localhost:8000/admin/jobs/upcoming
```

### Example Workflow 3: Manual Upload

```bash
# 1. Test AI generation first
curl -X POST http://localhost:8000/admin/actions/test-ai-generation \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "job_name": "test_ai_generation",
    "details": "Testing content generation for channel 1"
  }'

# 2. Queue a manual upload
curl -X POST "http://localhost:8000/admin/actions/queue-upload?channel_id=1" \
  -H "X-API-Key: your-api-key"

# Response:
# {
#   "message": "Upload queued successfully",
#   "job_id": 42
# }

# 3. Check upload history
curl -H "X-API-Key: your-api-key" \
  http://localhost:8000/admin/uploads/last
```

## Web Interface Features

The web interface provides:

1. **Real-time Updates**: Refresh buttons to reload data
2. **Modal Forms**: Clean interfaces for creating/editing resources
3. **Visual Status Indicators**: Color-coded badges for status (success, failure, active)
4. **Responsive Design**: Works on desktop and mobile devices
5. **Error Handling**: Clear error messages for failed operations
6. **Confirmation Dialogs**: Safety prompts before deleting resources

## Security Best Practices

1. **Set a Strong API Key**: Change `ADMIN_API_KEY` from the default value
   ```bash
   # In .env file
   ADMIN_API_KEY=your-very-secure-random-key-here
   ```

2. **Use HTTPS in Production**: Never expose admin endpoints over HTTP in production

3. **Restrict Access**: Use firewall rules or reverse proxy authentication to limit who can access the admin dashboard

4. **Regular Audits**: Monitor the job history for suspicious activity

5. **Rotate Credentials**: Periodically change API keys and OAuth tokens

## Troubleshooting

### Cannot access admin dashboard
- Verify the server is running: `curl http://localhost:8000/health`
- Check if the static file exists: `ls src/static/admin.html`

### Authentication fails
- Ensure `ADMIN_API_KEY` is set in your `.env` file
- Verify you're using the correct API key value
- Check the header name is exactly `X-API-Key`

### No upcoming jobs shown
- Verify schedules are marked as active
- Check that the scheduler is running via the system status endpoint
- Review scheduler logs for errors

### Upload fails
- Ensure YouTube OAuth is completed for the channel
- Verify YouTube credentials are configured
- Check job history for detailed error messages
