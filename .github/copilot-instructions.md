# RepoRadar AI Coding Guidelines

## Architecture Overview
RepoRadar is a Flask-based GitHub repository transfer monitoring system with component-based architecture:

- **`app.py`** - Main application with Flask routes, background scheduling, and component initialization
- **`github_tracker.py`** - GitHub API client handling rate limits and ownership detection
- **`database.py`** - SQLite database manager with transfer storage and statistics
- **`slack_notifier.py`** - Webhook-based notification system for high-value transfers

## Key Patterns & Conventions

### Configuration Management
- Use YAML config files (`config.yaml`) with `config.example.yaml` as template
- Support environment variable overrides (e.g., `PORT`, `DEBUG`, `DATABASE_PATH`)
- Access config via global `config` dict loaded in `initialize_components()`

### Component Initialization
```python
# Always initialize components in this order in app.py
config = load_config()
db = RepoRadarDB(config.get('database_path', 'reporadar.db'))
github_tracker = GitHubTracker(github_token, db)
slack_notifier = SlackNotifier(slack_webhook)
```

### Database Operations
- Use SQLite with `UNIQUE` constraints to prevent duplicate transfers
- Implement `INSERT OR IGNORE` for idempotent operations
- Return dicts from query methods using `sqlite3.Row`

### GitHub API Handling
- Implement rate limit checking with `X-RateLimit-Remaining` header
- Sleep automatically when approaching limits using `X-RateLimit-Reset`
- Add 0.1s delays between requests to be API-friendly
- Handle 404s gracefully for missing repositories

### Background Processing
- Use `schedule` library for periodic tasks (default: 15-minute polling)
- Run scheduler in daemon thread to avoid blocking Flask
- Check `schedule.run_pending()` every 60 seconds

### Error Handling & Logging
- Use structured logging with `logger.info/error/warning`
- Log component initialization status
- Handle API failures gracefully without crashing
- Return `None`/`False` on failures rather than raising exceptions

### Web Interface
- Use inline HTML templates in Flask routes (see `FEED_TEMPLATE`)
- Implement JSON API endpoints with consistent response format:
```python
return jsonify({
    'status': 'success',
    'data': result_data,
    'timestamp': datetime.now().isoformat()
})
```

## Development Workflow

### Local Development
```bash
# Setup
cp config.example.yaml config.yaml
pip install -r requirements.txt

# Configure GitHub token and Slack webhook in config.yaml
# Run locally
python app.py
```

### Docker Development
```bash
# Use docker-compose for consistent environment
docker-compose up -d

# View logs
docker-compose logs -f reporadar

# Debug with shell access
docker-compose exec reporadar bash
```

### Testing Transfers
- Manually trigger checks by calling `check_repositories()` with test repo list
- Use `/health` endpoint to verify component initialization
- Monitor logs for rate limit warnings and transfer detections

## Deployment Considerations

### Docker Best Practices
- Mount config as read-only volume: `./config.yaml:/app/config.yaml:ro`
- Use named volumes for data persistence: `reporadar_data:/app/data`
- Set `DATABASE_PATH` environment variable for containerized SQLite
- Include health checks in docker-compose for monitoring

### Production Configuration
- Set `DEBUG=false` in production
- Use secure webhook URLs for Slack notifications
- Configure appropriate polling intervals (15-60 minutes)
- Monitor rate limit usage and adjust polling frequency accordingly

## Common Patterns

### Transfer Detection Logic
```python
# Check ownership changes by comparing expected vs actual owner
expected_owner, repo_name = repo_full_name.split('/')
if expected_owner.lower() != current_owner.lower():
    # Record transfer
```

### Alert Filtering
```python
# Alert on high-star repos or target buyers
if stars >= min_stars or new_owner in target_buyers:
    send_slack_alert(transfer)
```

### API Response Handling
```python
response = self.session.get(url)
if response.status_code == 200:
    return response.json()
elif response.status_code == 404:
    return None  # Handle missing resources gracefully
```

## File Structure Expectations
- Keep database operations in `database.py`
- Isolate GitHub API logic in `github_tracker.py`
- Handle notifications in `slack_notifier.py`
- Reserve `app.py` for Flask routing and scheduling orchestration</content>
<parameter name="filePath">/workspaces/RepoRadar/.github/copilot-instructions.md