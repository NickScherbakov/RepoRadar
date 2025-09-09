"""RepoRadar: GitHub repository transfer tracking application."""

import os
import logging
import yaml
import schedule
import time
import threading
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request

from database import RepoRadarDB
from github_tracker import GitHubTracker
from slack_notifier import SlackNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Global variables for components
db = None
github_tracker = None
slack_notifier = None
config = {}


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Config file {config_path} not found. Using example config.")
        with open("config.example.yaml", 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}


def initialize_components():
    """Initialize database, GitHub tracker, and Slack notifier."""
    global db, github_tracker, slack_notifier, config
    
    config = load_config()
    
    # Initialize database
    db_path = config.get('database_path', 'reporadar.db')
    db = RepoRadarDB(db_path)
    
    # Initialize GitHub tracker
    github_token = config.get('github', {}).get('token')
    if not github_token or github_token == "your_github_token_here":
        logger.error("GitHub token not configured!")
        return False
        
    github_tracker = GitHubTracker(github_token, db)
    
    # Initialize Slack notifier
    slack_webhook = config.get('slack', {}).get('webhook_url')
    slack_notifier = SlackNotifier(slack_webhook)
    
    logger.info("All components initialized successfully")
    return True


def check_repositories():
    """Scheduled function to check repositories for transfers."""
    logger.info("Starting repository check...")
    
    try:
        # Get repositories and organizations from config
        repositories = config.get('repositories', [])
        organizations = config.get('organizations', [])
        
        all_transfers = []
        
        # Check specific repositories
        if repositories:
            transfers = github_tracker.check_repositories(repositories)
            all_transfers.extend(transfers)
        
        # Check organization repositories
        if organizations:
            transfers = github_tracker.check_organizations(organizations)
            all_transfers.extend(transfers)
        
        # Send Slack alerts for qualifying transfers
        if all_transfers:
            alerts_config = config.get('alerts', {})
            min_stars = alerts_config.get('min_stars', 1000)
            target_buyers = alerts_config.get('target_buyers', [])
            
            slack_notifier.send_batch_alert(all_transfers, target_buyers, min_stars)
            
        logger.info(f"Repository check completed. Found {len(all_transfers)} transfers.")
        
    except Exception as e:
        logger.error(f"Error during repository check: {e}")


def start_scheduler():
    """Start the background scheduler for repository polling."""
    poll_interval = config.get('poll_interval', 15)
    schedule.every(poll_interval).minutes.do(check_repositories)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info(f"Scheduler started. Polling every {poll_interval} minutes.")


# HTML template for the feed page
FEED_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>RepoRadar - Repository Transfer Feed</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }
        .transfer { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; background: #fafafa; }
        .transfer-header { font-weight: bold; color: #333; margin-bottom: 5px; }
        .transfer-details { font-size: 14px; color: #666; }
        .stars { color: #f39c12; font-weight: bold; }
        .language { background: #3498db; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px; }
        .date { color: #95a5a6; font-size: 12px; }
        .no-transfers { text-align: center; color: #999; padding: 40px; }
        .refresh-btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .refresh-btn:hover { background: #2980b9; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 RepoRadar - Repository Transfer Feed</h1>
            <p>Tracking GitHub repository ownership changes and acquisitions</p>
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
        </div>
        
        {% if transfers %}
            {% for transfer in transfers %}
            <div class="transfer">
                <div class="transfer-header">
                    📦 <a href="https://github.com/{{ transfer.repo }}" target="_blank">{{ transfer.repo }}</a>
                </div>
                <div class="transfer-details">
                    <strong>{{ transfer.old_owner }}</strong> → <strong>{{ transfer.new_owner }}</strong>
                    {% if transfer.stars > 0 %}
                        | <span class="stars">⭐ {{ "{:,}".format(transfer.stars) }}</span>
                    {% endif %}
                    {% if transfer.language %}
                        | <span class="language">{{ transfer.language }}</span>
                    {% endif %}
                </div>
                <div class="date">{{ transfer.date[:19] }}</div>
            </div>
            {% endfor %}
        {% else %}
            <div class="no-transfers">
                <h3>No transfers detected yet</h3>
                <p>RepoRadar is monitoring your configured repositories. Check back later!</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    """Redirect to feed page."""
    return '<h1>RepoRadar</h1><p><a href="/feed">View Transfer Feed</a> | <a href="/stats">View Statistics</a></p>'


@app.route('/feed')
def feed():
    """HTML feed page showing recent repository transfers."""
    transfers = db.get_transfers(limit=50)
    return render_template_string(FEED_TEMPLATE, transfers=transfers)


@app.route('/stats')
def stats():
    """JSON statistics endpoint."""
    stats = db.get_stats()
    return jsonify({
        'status': 'success',
        'data': stats,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/export')
def export_data():
    """Export all transfer data as JSON for dashboard generation."""
    try:
        transfers = db.get_transfers(limit=1000)  # Получить последние 1000 переносов
        return jsonify({
            'status': 'success',
            'data': transfers,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'database': db is not None,
            'github_tracker': github_tracker is not None,
            'slack_notifier': slack_notifier is not None
        }
    })


if __name__ == '__main__':
    # Initialize components
    if not initialize_components():
        logger.error("Failed to initialize components. Exiting.")
        exit(1)
    
    # Start background scheduler
    start_scheduler()
    
    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting RepoRadar on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)