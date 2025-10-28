"""
Outlook Email Scanner Module

WHAT: Scans Outlook folders for emails with attachments and downloads them
WHY: Automates finding and extracting seller data files from email
HOW: Uses Microsoft Graph API to query mailbox and download attachments

USAGE:
    scanner = OutlookScanner(folder_name="Data Tape Import")
    emails = scanner.scan(days_back=7, unread_only=True)

    for email in emails:
        files = scanner.download_attachments(email, seller_rules)
        if mark_read:
            scanner.mark_as_read(email['id'])
"""

import os
import base64
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta

import requests
from msal import ConfidentialClientApplication

from .seller_rules import SellerRule

logger = logging.getLogger(__name__)


class OutlookScanner:
    """
    WHAT: Handles all Outlook/Microsoft Graph API operations
    WHY: Centralized email scanning and attachment downloading
    HOW: Uses MSAL for authentication and Graph API for operations
    """

    def __init__(self, folder_name: Optional[str] = None, stdout=None):
        """
        Initialize Outlook scanner

        Args:
            folder_name: Outlook folder to scan (default: Inbox)
            stdout: Django stdout for progress messages (optional)
        """
        self.folder_name = folder_name or 'Inbox'
        self.stdout = stdout
        self.access_token = None
        self.user_email = os.getenv('MICROSOFT_USER_EMAIL')

        if not self.user_email:
            raise ValueError('MICROSOFT_USER_EMAIL not found in .env file')

    def _get_access_token(self) -> str:
        """
        WHAT: Authenticate with Microsoft Graph API and get access token
        WHY: Required to access Outlook mailbox via Microsoft Graph API
        HOW: Uses MSAL (Microsoft Authentication Library) with client credentials flow

        DOCS: https://learn.microsoft.com/en-us/graph/auth-v2-service

        Returns:
            Access token string

        Raises:
            ValueError: If credentials missing or authentication fails
        """
        if self.access_token:
            return self.access_token

        client_id = os.getenv('MICROSOFT_CLIENT_ID')
        client_secret = os.getenv('MICROSOFT_CLIENT_SECRET')
        tenant_id = os.getenv('MICROSOFT_TENANT_ID')

        if not all([client_id, client_secret, tenant_id]):
            raise ValueError(
                'Microsoft Graph credentials not found in .env file. Required:\n'
                '  - MICROSOFT_CLIENT_ID\n'
                '  - MICROSOFT_CLIENT_SECRET\n'
                '  - MICROSOFT_TENANT_ID'
            )

        authority = f"https://login.microsoftonline.com/{tenant_id}"
        app = ConfidentialClientApplication(
            client_id,
            authority=authority,
            client_credential=client_secret,
        )

        # Request token with Mail.Read scope
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

        if "access_token" not in result:
            error_msg = result.get("error_description", result.get("error", "Unknown error"))
            raise ValueError(f'Failed to acquire access token: {error_msg}')

        self.access_token = result["access_token"]
        return self.access_token

    def scan(
        self,
        days_back: int = 2,
        unread_only: bool = False,
        subject_filter: Optional[str] = None,
        sender_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        WHAT: Scan Outlook folder for emails with attachments
        WHY: Find seller data emails automatically
        HOW: Uses Microsoft Graph API to query mailbox folder

        DOCS: https://learn.microsoft.com/en-us/graph/api/user-list-messages

        Args:
            days_back: Number of days to look back (default: 7)
            unread_only: Only return unread emails (default: False)
            subject_filter: Comma-separated keywords to filter by subject
            sender_filter: Comma-separated email addresses to filter by sender

        Returns:
            List of email dicts with id, subject, from, receivedDateTime, body
        """
        access_token = self._get_access_token()

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        # Build filter criteria
        filters = []
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%dT00:00:00Z')
        filters.append(f"receivedDateTime ge {start_date}")

        if unread_only:
            filters.append("isRead eq false")

        filters.append("hasAttachments eq true")
        filter_query = " and ".join(filters)

        # Find folder and get messages
        url = self._get_folder_url(headers)

        params = {
            '$filter': filter_query,
            '$select': 'id,subject,from,receivedDateTime,hasAttachments,body',
            '$orderby': 'receivedDateTime desc',
            '$top': 50,
        }

        if self.stdout:
            folder_display = f'"{self.folder_name}"' if self.folder_name != 'Inbox' else 'Inbox'
            self.stdout.write(f'Querying Outlook folder {folder_display} (last {days_back} days)...')

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise ValueError(f'Failed to query emails: {response.status_code} - {response.text}')

        emails = response.json().get('value', [])

        if self.stdout:
            self.stdout.write(f'   [OK] Found {len(emails)} emails with attachments\n')

        # Apply additional filters
        filtered_emails = []
        for email in emails:
            # Subject filter
            if subject_filter:
                keywords = [k.strip() for k in subject_filter.split(',')]
                subject = email.get('subject', '').lower()
                if not any(keyword.lower() in subject for keyword in keywords):
                    continue

            # Sender filter
            if sender_filter:
                allowed_senders = [s.strip().lower() for s in sender_filter.split(',')]
                sender_email = email.get('from', {}).get('emailAddress', {}).get('address', '').lower()
                if sender_email not in allowed_senders:
                    continue

            filtered_emails.append(email)

        if subject_filter or sender_filter:
            if self.stdout:
                self.stdout.write(f'   Emails matching filters: {len(filtered_emails)}\n')

        return filtered_emails

    def _get_folder_url(self, headers: Dict[str, str]) -> str:
        """
        WHAT: Get Graph API URL for messages in specified folder
        WHY: Folder may be Inbox or custom folder by name
        HOW: Search for folder by displayName if not Inbox

        Args:
            headers: HTTP headers with Authorization token

        Returns:
            Graph API URL for messages endpoint
        """
        if self.folder_name and self.folder_name.lower() != 'inbox':
            # Search for folder by name
            folder_url = f"https://graph.microsoft.com/v1.0/users/{self.user_email}/mailFolders"
            folder_params = {'$filter': f"displayName eq '{self.folder_name}'"}
            folder_response = requests.get(folder_url, headers=headers, params=folder_params)

            if folder_response.status_code == 200:
                folders = folder_response.json().get('value', [])
                if folders:
                    folder_id = folders[0]['id']
                    return f"https://graph.microsoft.com/v1.0/users/{self.user_email}/mailFolders/{folder_id}/messages"
                else:
                    if self.stdout:
                        self.stdout.write(f'   [WARNING] Folder "{self.folder_name}" not found. Using Inbox instead.\n')

        # Default to Inbox
        return f"https://graph.microsoft.com/v1.0/users/{self.user_email}/messages"

    def download_attachments(
        self,
        email: Dict[str, Any],
        seller_rule: Optional[SellerRule] = None
    ) -> List[Tuple[Path, Optional[str]]]:
        """
        WHAT: Download Excel attachments from an email
        WHY: Need local file to process with pandas
        HOW: Uses Microsoft Graph API to download attachments to temp directory

        DOCS: https://learn.microsoft.com/en-us/graph/api/attachment-get

        Args:
            email: Email data from Microsoft Graph
            seller_rule: Optional seller rules for password extraction and filtering

        Returns:
            List of tuples: (file_path, password)
        """
        access_token = self._get_access_token()
        email_id = email['id']

        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        # Get attachments
        url = f"https://graph.microsoft.com/v1.0/users/{self.user_email}/messages/{email_id}/attachments"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            if self.stdout:
                self.stdout.write(f'   [ERROR] Failed to get attachments: {response.status_code}\n')
            return []

        attachments = response.json().get('value', [])

        # Extract password using seller-specific rules
        password = None
        if seller_rule:
            password = seller_rule.extract_password(email)
            if password and self.stdout:
                self.stdout.write(f'   Found password using {seller_rule.name} rule: {password}\n')

        # Download Excel files
        downloaded_files = []

        for attachment in attachments:
            filename = attachment.get('name', '')
            file_ext = Path(filename).suffix.lower()

            # Only process Excel files
            if file_ext not in ['.xlsx', '.xls', '.csv']:
                continue

            # Apply seller-specific attachment filter
            if seller_rule and not seller_rule.matches_attachment(filename):
                if self.stdout:
                    self.stdout.write(f'   Skipping attachment (does not match filter): {filename}\n')
                continue

            if self.stdout:
                self.stdout.write(f'   Downloading attachment: {filename}\n')

            # Get attachment content
            content_bytes = attachment.get('contentBytes')
            if not content_bytes:
                if self.stdout:
                    self.stdout.write(f'      [WARNING] No content for {filename}\n')
                continue

            # Save to temp file
            temp_dir = Path(tempfile.gettempdir()) / 'outlook_etl'
            temp_dir.mkdir(exist_ok=True)

            temp_file = temp_dir / filename
            with open(temp_file, 'wb') as f:
                f.write(base64.b64decode(content_bytes))

            if self.stdout:
                self.stdout.write(f'      [OK] Saved to: {temp_file}\n')

            downloaded_files.append((temp_file, password))

        return downloaded_files

    def mark_as_read(self, email_id: str):
        """
        WHAT: Mark an email as read in Outlook
        WHY: Prevents reprocessing the same email multiple times
        HOW: Uses Microsoft Graph API PATCH request

        Args:
            email_id: Email ID from Microsoft Graph
        """
        access_token = self._get_access_token()

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        url = f"https://graph.microsoft.com/v1.0/users/{self.user_email}/messages/{email_id}"
        data = {'isRead': True}

        response = requests.patch(url, headers=headers, json=data)

        if response.status_code == 200:
            if self.stdout:
                self.stdout.write('   Marked email as read\n')
        else:
            logger.warning(f'Failed to mark email as read: {response.status_code}')
