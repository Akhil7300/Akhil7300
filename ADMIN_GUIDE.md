# Admin Dashboard Guide

This guide provides comprehensive documentation for administrators using the Admin Dashboard to manage YouTube automation workflows.

## Table of Contents

- [Getting Started](#getting-started)
- [Configuration Management](#configuration-management)
- [Scheduling](#scheduling)
- [Monitoring](#monitoring)
- [Manual Actions](#manual-actions)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Getting Started

### First Time Setup

1. **Configure Environment Variables**

   Copy the template and fill in your credentials:
   ```bash
   cp .env.template .env
   ```

   Critical settings:
   - `ADMIN_API_KEY`: Set a strong, unique API key
   - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: For AI content generation
   - `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET`: For YouTube OAuth

2. **Start the Server**

   ```bash
   poetry run uvicorn src.main:app --reload
   ```

3. **Access the Dashboard**

   Open http://localhost:8000/admin/dashboard in your browser and enter your API key.

### API Authentication

All API requests require the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key-here" http://localhost:8000/admin/status
```

## Configuration Management

### Channel Configuration

Channels represent YouTube channels you want to manage. Each channel has:

- **Channel Name**: Human-readable name for identification
- **Channel ID**: YouTube channel ID (format: UC_XXXXX)
- **Content Type**: Type of content (educational, entertainment, tutorial, review)
- **Video Length**: Target length (short: <1min, medium: 1-5min, long: >5min)
- **Video Style**: Content style (informative, casual, professional, humorous)
- **AI Provider**: Which AI service to use (openai, anthropic)
- **YouTube Connection**: Whether OAuth is completed

#### Content Type Guidelines

- **Educational**: Instructional content, how-tos, explanations
- **Entertainment**: Fun, engaging content for general audiences
- **Tutorial**: Step-by-step guides and walkthroughs
- **Review**: Product reviews, comparisons, analysis

#### Video Style Guidelines

- **Informative**: Fact-based, clear, straightforward
- **Casual**: Friendly, conversational tone
- **Professional**: Formal, business-appropriate
- **Humorous**: Light-hearted, entertaining

### Schedule Configuration

Schedules control when automated uploads occur:

- **Frequency**: How often to upload
  - `daily`: Every day at the specified time
  - `weekly`: Once per week
  - `monthly`: Once per month

- **Preferred Time**: Time of day (24-hour format: HH:MM)
- **Timezone**: Timezone for the schedule (e.g., UTC, EST, PST)
- **Active**: Whether the schedule is currently enabled

#### Scheduling Best Practices

1. **Optimal Upload Times**: Research your audience's active hours
2. **Consistency**: Maintain regular upload schedules
3. **Time Zones**: Consider your primary audience location
4. **Testing**: Start with inactive schedules to test workflows

## Monitoring

### System Status

The system status endpoint provides an overview:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/admin/status
```

Key metrics:
- Total channels configured
- Active schedules
- Recent job count
- Failed job count
- AI provider availability
- YouTube configuration status

### Job History

Track all background job executions:

- **Job Name**: Identifier for the job
- **Job Type**: `scheduled` (automatic) or `manual` (triggered by admin)
- **Status**: `success`, `failure`, or `running`
- **Start/End Time**: When the job executed
- **Details**: Additional information about the job
- **Error Message**: If failed, why it failed

#### Common Job Types

- `upload_channel_X`: Video upload job for channel X
- `generate_content_X`: Content generation for channel X
- `test_ai_generation`: Manual AI test
- `manual_upload_X`: Manually triggered upload

### Upload History

Track all video upload attempts:

- **Video Title**: Title of the uploaded video
- **Video ID**: YouTube video ID (if successful)
- **Status**: Upload success/failure
- **Upload Time**: When the upload occurred
- **Error Message**: Reason for failure (if any)

### Upcoming Jobs

View scheduled jobs that will run in the future. This shows:
- Next run time
- Trigger configuration (cron expression)
- Job name/ID

## Manual Actions

### Triggering YouTube OAuth

Before uploads can work, you must authorize YouTube access:

1. **Get OAuth URL**
   ```bash
   curl -X POST "http://localhost:8000/admin/actions/trigger-oauth?channel_id=1" \
     -H "X-API-Key: your-api-key"
   ```

2. **Visit the URL**: Open the returned `oauth_url` in a browser

3. **Grant Permissions**: Authorize the application to access YouTube

4. **Verify**: Check the channel's `youtube_connected` status

### Testing AI Generation

Before scheduling automated uploads, test AI generation:

```bash
curl -X POST http://localhost:8000/admin/actions/test-ai-generation \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "job_name": "test_ai_generation",
    "details": "Testing with new configuration"
  }'
```

Check the job history to see results.

### Queuing Manual Uploads

Trigger an immediate upload without waiting for the schedule:

```bash
curl -X POST "http://localhost:8000/admin/actions/queue-upload?channel_id=1" \
  -H "X-API-Key: your-api-key"
```

This is useful for:
- Testing new configurations
- Recovering from failed uploads
- Publishing time-sensitive content

## Best Practices

### Security

1. **Strong API Key**: Use a random, complex API key (32+ characters)
   ```bash
   # Generate a secure key
   openssl rand -hex 32
   ```

2. **HTTPS in Production**: Never expose the admin dashboard over HTTP

3. **Firewall Rules**: Restrict admin endpoint access by IP if possible

4. **Regular Audits**: Review job history for suspicious activity

5. **Credential Rotation**: Change API keys and OAuth tokens periodically

### Reliability

1. **Monitor Failed Jobs**: Set up alerts for job failures

2. **Test Before Scheduling**: Always test manually before enabling schedules

3. **Backup Configuration**: Export channel and schedule configurations

4. **Gradual Rollout**: Start with one channel before scaling

### Performance

1. **Appropriate Video Length**: Match length to content complexity

2. **AI Provider Selection**: 
   - OpenAI: Generally faster, good for quick content
   - Anthropic: Often more detailed, better for longer content

3. **Schedule Spacing**: Don't schedule too many uploads simultaneously

## Troubleshooting

### Common Issues

#### "Invalid API Key" Error

**Problem**: Authentication fails when accessing admin endpoints

**Solutions**:
1. Verify `ADMIN_API_KEY` is set in `.env`
2. Check for typos in the API key
3. Ensure header is exactly `X-API-Key` (case-sensitive)
4. Restart the server after changing `.env`

#### YouTube Connection Fails

**Problem**: Unable to complete OAuth flow

**Solutions**:
1. Verify `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET` are set
2. Ensure redirect URI matches: `http://localhost:8000/admin/oauth/callback`
3. Check Google Cloud Console OAuth configuration
4. Verify YouTube Data API is enabled in Google Cloud

#### Scheduled Jobs Not Running

**Problem**: Jobs don't execute at scheduled times

**Solutions**:
1. Check scheduler status: `curl -H "X-API-Key: key" http://localhost:8000/admin/status`
2. Verify schedule is marked as `is_active: true`
3. Check timezone configuration
4. Review server logs for scheduler errors

#### AI Generation Fails

**Problem**: AI content generation returns errors

**Solutions**:
1. Verify API key is valid: Check `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
2. Check API quota/credits
3. Review job history error messages
4. Test with simpler prompts first

#### Upload Fails

**Problem**: Video upload to YouTube fails

**Solutions**:
1. Ensure YouTube OAuth is completed (`youtube_connected: true`)
2. Check YouTube API quotas
3. Verify video file format and size
4. Review upload history error messages

### Debug Mode

For detailed logging, set environment variable:

```bash
ENV=development
```

This enables:
- Verbose SQL queries
- Detailed error traces
- Request/response logging

### Getting Help

1. **Check Logs**: Review `/tmp/server.log` for errors
2. **Job History**: Look for detailed error messages
3. **System Status**: Verify all components are operational
4. **Documentation**: Review README.md and SCREENSHOTS.md

## Advanced Usage

### Bulk Operations

Create multiple channels programmatically:

```bash
for channel in channel1 channel2 channel3; do
  curl -X POST http://localhost:8000/admin/channels \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"channel_name\": \"$channel\",
      \"channel_id\": \"UC_${channel}\",
      \"content_type\": \"educational\"
    }"
done
```

### Monitoring Integration

Export metrics for monitoring systems:

```bash
# Get system status in JSON
curl -H "X-API-Key: $API_KEY" http://localhost:8000/admin/status > metrics.json

# Count failed jobs in last 24 hours
curl -H "X-API-Key: $API_KEY" http://localhost:8000/admin/jobs/history?limit=100 \
  | jq '[.[] | select(.status == "failure")] | length'
```

### Backup and Restore

Export all configurations:

```bash
# Backup channels
curl -H "X-API-Key: $API_KEY" http://localhost:8000/admin/channels > channels_backup.json

# Backup schedules
curl -H "X-API-Key: $API_KEY" http://localhost:8000/admin/schedules > schedules_backup.json
```

## API Reference Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/status` | GET | System status overview |
| `/admin/channels` | GET | List all channels |
| `/admin/channels` | POST | Create new channel |
| `/admin/channels/{id}` | GET | Get channel details |
| `/admin/channels/{id}` | PUT | Update channel |
| `/admin/channels/{id}` | DELETE | Delete channel |
| `/admin/schedules` | GET | List all schedules |
| `/admin/schedules` | POST | Create schedule |
| `/admin/schedules/{id}` | PUT | Update schedule |
| `/admin/schedules/{id}` | DELETE | Delete schedule |
| `/admin/jobs/history` | GET | View job history |
| `/admin/jobs/upcoming` | GET | View scheduled jobs |
| `/admin/uploads/history` | GET | View upload history |
| `/admin/uploads/last` | GET | Get last upload |
| `/admin/actions/trigger-oauth` | POST | Initiate YouTube OAuth |
| `/admin/actions/test-ai-generation` | POST | Test AI generation |
| `/admin/actions/queue-upload` | POST | Queue manual upload |

For detailed API documentation, visit http://localhost:8000/docs

## Conclusion

The Admin Dashboard provides comprehensive control over your YouTube automation workflow. Start with manual testing, gradually enable schedules, and monitor results regularly for best results.

For additional examples and visual guides, see [SCREENSHOTS.md](SCREENSHOTS.md).
