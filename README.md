# RepoRadar 🔍

RepoRadar tracks GitHub repository transfers in real time and turns them into early M&A signals. Startups see what tech and teams are getting scooped up; investors get alerts on stealth acquisitions and acqui-hires before the press release.

## Features

- 🔄 **Automated Monitoring**: Polls GitHub API every 15 minutes for repository ownership changes
- 📊 **SQLite Storage**: Tracks transfers with repo, old_owner, new_owner, date, stars, and language
- 🚨 **Smart Alerts**: Slack notifications for high-value repos (≥1000 stars) or big tech acquisitions
- 🌐 **Web Interface**: Clean HTML feed and JSON stats API
- 🐳 **Docker Ready**: One-command deployment with Docker
- ⚡ **Lightweight**: Minimal dependencies, efficient resource usage

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/NickScherbakov/RepoRadar.git
cd RepoRadar
pip install -r requirements.txt
```

### 2. Configure

Copy the example config and customize:

```bash
cp config.example.yaml config.yaml
```

Edit `config.yaml` with your settings:

```yaml
github:
  token: "your_github_personal_access_token"

repositories:
  - "facebook/react"
  - "microsoft/vscode"

organizations:
  - "openai"
  - "anthropic"

slack:
  webhook_url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"

alerts:
  min_stars: 1000
  target_buyers:
    - "google"
    - "meta" 
    - "amazon"
    - "microsoft"
    - "apple"
```

### 3. Run

```bash
python app.py
```

Visit `http://localhost:5000/feed` to see the transfer feed.

## Docker Deployment

### Build and Run

```bash
docker build -t reporadar .
docker run -d -p 5000:5000 -v $(pwd)/config.yaml:/app/config.yaml -v reporadar_data:/app/data reporadar
```

### Docker Compose (Recommended)

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  reporadar:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./config.yaml:/app/config.yaml
      - reporadar_data:/app/data
    restart: unless-stopped
    
volumes:
  reporadar_data:
```

Run with:
```bash
docker-compose up -d
```

## API Endpoints

- **`GET /`** - Home page with navigation
- **`GET /feed`** - HTML feed of recent repository transfers  
- **`GET /stats`** - JSON statistics about transfers
- **`GET /health`** - Health check endpoint

### Example Stats Response

```json
{
  "status": "success",
  "data": {
    "total_transfers": 42,
    "unique_buyers": 15,
    "unique_sellers": 38,
    "avg_stars": 2847,
    "max_stars": 50000,
    "top_buyers": [
      {"new_owner": "microsoft", "count": 8},
      {"new_owner": "google", "count": 5}
    ]
  },
  "timestamp": "2025-01-09T12:34:56"
}
```

## Configuration

### GitHub Token

Create a [GitHub Personal Access Token](https://github.com/settings/tokens) with `public_repo` scope.

### Slack Integration (Optional)

1. Create a [Slack Incoming Webhook](https://api.slack.com/messaging/webhooks)
2. Add the webhook URL to your config
3. Customize alert thresholds

### Monitoring Options

- **Specific Repositories**: List exact repo names to monitor
- **Organizations**: Monitor all public repos in an organization
- **Polling Interval**: Adjust check frequency (default: 15 minutes)

## Database Schema

SQLite table `repo_transfers`:

```sql
CREATE TABLE repo_transfers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo TEXT NOT NULL,
    old_owner TEXT NOT NULL, 
    new_owner TEXT NOT NULL,
    date TEXT NOT NULL,
    stars INTEGER DEFAULT 0,
    language TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(repo, old_owner, new_owner, date)
);
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest

# Run tests
pytest
```

### Environment Variables

- `PORT`: Server port (default: 5000)
- `DEBUG`: Enable debug mode (default: False)
- `DATABASE_PATH`: SQLite database path

## Rate Limiting

RepoRadar respects GitHub API rate limits:
- Monitors remaining requests
- Automatically sleeps when limits approached
- Uses efficient polling strategies

## License

MIT License - see [LICENSE](LICENSE) file.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

- 📧 [Open an issue](https://github.com/NickScherbakov/RepoRadar/issues) for bug reports
- 💡 [Discussion forum](https://github.com/NickScherbakov/RepoRadar/discussions) for questions
- ⭐ Star the repo if you find it useful!