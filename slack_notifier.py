"""Slack notification module for RepoRadar."""

import requests
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Slack webhook notifier for repository transfer alerts."""

    def __init__(self, webhook_url: Optional[str] = None):
        """Initialize Slack notifier with webhook URL."""
        self.webhook_url = webhook_url
        self.enabled = webhook_url is not None

    def send_message(self, message: str, title: str = "RepoRadar Alert") -> bool:
        """Send a message to Slack."""
        if not self.enabled:
            logger.warning("Slack notifications not configured")
            return False

        payload = {
            "text": title,
            "attachments": [
                {
                    "color": "warning",
                    "text": message,
                    "mrkdwn_in": ["text"]
                }
            ]
        }

        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info("Slack notification sent successfully")
                return True
            else:
                logger.error(f"Slack notification failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            return False

    def should_alert(self, transfer: Dict, target_buyers: List[str], min_stars: int = 1000) -> bool:
        """Check if a transfer should trigger an alert."""
        stars = transfer.get('stars', 0)
        new_owner = transfer.get('new_owner', '').lower()
        
        # Alert if stars >= threshold
        if stars >= min_stars:
            return True
            
        # Alert if buyer matches target list
        for buyer in target_buyers:
            if buyer.lower() in new_owner:
                return True
                
        return False

    def format_transfer_message(self, transfer: Dict) -> str:
        """Format a repository transfer into a Slack message."""
        repo = transfer.get('repo', 'Unknown')
        old_owner = transfer.get('old_owner', 'Unknown')
        new_owner = transfer.get('new_owner', 'Unknown')
        stars = transfer.get('stars', 0)
        language = transfer.get('language', 'Unknown')
        
        message = f"🚨 *Repository Transfer Detected*\n\n"
        message += f"*Repository:* `{repo}`\n"
        message += f"*From:* {old_owner}\n"
        message += f"*To:* {new_owner}\n"
        message += f"*Stars:* ⭐ {stars:,}\n"
        message += f"*Language:* {language}\n"
        message += f"*GitHub:* https://github.com/{repo}"
        
        return message

    def send_transfer_alert(self, transfer: Dict, target_buyers: List[str], min_stars: int = 1000) -> bool:
        """Send an alert for a repository transfer if it meets criteria."""
        if not self.should_alert(transfer, target_buyers, min_stars):
            return False

        message = self.format_transfer_message(transfer)
        return self.send_message(message, "🔔 High-Value Repository Transfer")

    def send_batch_alert(self, transfers: List[Dict], target_buyers: List[str], min_stars: int = 1000) -> bool:
        """Send a batch alert for multiple transfers."""
        qualifying_transfers = [
            t for t in transfers 
            if self.should_alert(t, target_buyers, min_stars)
        ]
        
        if not qualifying_transfers:
            return False

        if len(qualifying_transfers) == 1:
            return self.send_transfer_alert(qualifying_transfers[0], target_buyers, min_stars)

        # Multiple transfers
        message = f"🚨 *{len(qualifying_transfers)} High-Value Repository Transfers Detected*\n\n"
        
        for i, transfer in enumerate(qualifying_transfers[:10], 1):  # Limit to 10 for message size
            repo = transfer.get('repo', 'Unknown')
            old_owner = transfer.get('old_owner', 'Unknown')
            new_owner = transfer.get('new_owner', 'Unknown')
            stars = transfer.get('stars', 0)
            
            message += f"{i}. `{repo}` ({old_owner} → {new_owner}) ⭐ {stars:,}\n"
        
        if len(qualifying_transfers) > 10:
            message += f"\n...and {len(qualifying_transfers) - 10} more transfers"
            
        return self.send_message(message, "🔔 Multiple Repository Transfers")