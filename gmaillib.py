"""
Modern Python Gmail Library

A Python 3 library for interacting with Gmail using IMAP and SMTP protocols.
Supports both traditional password authentication and OAuth2.
"""

import imaplib
import smtplib
import email
from email import policy
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import List, Optional, Tuple, Union
from dataclasses import dataclass
import base64
from contextlib import contextmanager


class GmailLibError(Exception):
    """Base exception for gmaillib errors"""
    pass


class AuthenticationError(GmailLibError):
    """Raised when authentication fails"""
    pass


class ConnectionError(GmailLibError):
    """Raised when connection to Gmail servers fails"""
    pass


class MessageError(GmailLibError):
    """Raised when there's an issue with email message processing"""
    pass


@dataclass
class Message:
    """
    Represents an email message.

    Attributes:
        parsed_email: The parsed email message object
        receiver_addr: Email address of the receiver
        sender_addr: Email address of the sender
        date: Date the message was sent
        subject: Subject of the email
        body: Content of the email
    """

    def __init__(self, fetched_email: Union[str, bytes], **kwargs):
        """
        Initialize a message from fetched email data.

        Args:
            fetched_email: Raw email data as string or bytes
            **kwargs: Additional options
                types: List of acceptable content types (default: ['text/plain'])
        """
        accepted_types = kwargs.get('types', ['text/plain'])

        # Handle both bytes and string input
        if isinstance(fetched_email, bytes):
            parsed = email.message_from_bytes(fetched_email, policy=policy.default)
        else:
            parsed = email.message_from_string(fetched_email, policy=policy.default)

        self.parsed_email = parsed
        self.receiver_addr = parsed.get('to', '')
        self.sender_addr = parsed.get('from', '')
        self.date = parsed.get('date', '')
        self.subject = parsed.get('subject', '')
        self.body = ''

        if parsed.is_multipart():
            for part in parsed.walk():
                if part.get_content_type() in accepted_types:
                    try:
                        self.body = part.get_content()
                        break
                    except Exception:
                        # Fallback to get_payload for compatibility
                        self.body = part.get_payload(decode=True)
                        if isinstance(self.body, bytes):
                            self.body = self.body.decode('utf-8', errors='replace')
        else:
            if parsed.get_content_type() in accepted_types:
                try:
                    self.body = parsed.get_content()
                except Exception:
                    # Fallback to get_payload for compatibility
                    self.body = parsed.get_payload(decode=True)
                    if isinstance(self.body, bytes):
                        self.body = self.body.decode('utf-8', errors='replace')

    def __repr__(self) -> str:
        return f"<Msg from: {self.sender_addr}>"

    def __str__(self) -> str:
        return (f"To: {self.receiver_addr}\n"
                f"From: {self.sender_addr}\n"
                f"Date: {self.date}\n"
                f"Subject: {self.subject}\n\n"
                f"{self.body}")

    def download_attachment(self, dest_dir: str) -> str:
        """
        Download all attachments from the email to the specified directory.

        Args:
            dest_dir: Destination directory for attachments

        Returns:
            Status message
        """
        mail = self.parsed_email

        if mail.get_content_maintype() != 'multipart':
            return "no attachment"

        print(f"[{mail['From']}]: {mail['Subject']}")

        counter = 1
        for part in mail.walk():
            if part.get_content_maintype() == 'multipart':
                continue

            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()

            if not filename:
                filename = f'part-{counter:03d}.bin'
                counter += 1

            att_path = os.path.join(dest_dir, filename)

            if not os.path.isfile(att_path):
                with open(att_path, 'wb') as fp:
                    payload = part.get_payload(decode=True)
                    if payload:
                        fp.write(payload)

        return "attachments downloaded"


class Account:
    """
    Represents a Gmail account with methods to send and receive emails.

    Attributes:
        username: Gmail username/email address
        password: Password or OAuth2 access token
    """

    def __init__(self, username: str, password: Optional[str] = None,
                 oauth2_token: Optional[str] = None):
        """
        Initialize a Gmail account connection.

        Args:
            username: Gmail email address
            password: Account password (for basic auth)
            oauth2_token: OAuth2 access token (preferred over password)

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If connection to Gmail servers fails
        """
        self.username = username
        self.password = password
        self.oauth2_token = oauth2_token
        self.sendserver: Optional[smtplib.SMTP] = None
        self.receiveserver: Optional[imaplib.IMAP4_SSL] = None

        self._connect()

    def _connect(self):
        """Establish connections to SMTP and IMAP servers"""
        try:
            # Setup SMTP connection
            self.sendserver = smtplib.SMTP('smtp.gmail.com', 587)
            self.sendserver.starttls()

            # Setup IMAP connection
            self.receiveserver = imaplib.IMAP4_SSL('imap.gmail.com', 993)

            # Authenticate
            if self.oauth2_token:
                self._oauth2_login()
            elif self.password:
                self.sendserver.login(self.username, self.password)
                self.receiveserver.login(self.username, self.password)
            else:
                raise AuthenticationError("Either password or oauth2_token must be provided")

        except imaplib.IMAP4.error as e:
            raise AuthenticationError(f"IMAP authentication failed: {e}")
        except smtplib.SMTPAuthenticationError as e:
            raise AuthenticationError(f"SMTP authentication failed: {e}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Gmail: {e}")

    def _oauth2_login(self):
        """Authenticate using OAuth2 token"""
        if not self.oauth2_token or not self.receiveserver or not self.sendserver:
            raise AuthenticationError("OAuth2 token or server connection not available")

        # IMAP OAuth2 authentication
        auth_string = f'user={self.username}\x01auth=Bearer {self.oauth2_token}\x01\x01'
        auth_string_b64 = base64.b64encode(auth_string.encode()).decode()

        try:
            self.receiveserver.authenticate('XOAUTH2', lambda x: auth_string_b64)
        except Exception as e:
            raise AuthenticationError(f"OAuth2 IMAP authentication failed: {e}")

        # SMTP OAuth2 authentication
        try:
            self.sendserver.auth('XOAUTH2',
                               lambda: auth_string_b64,
                               initial_response_ok=True)
        except Exception as e:
            raise AuthenticationError(f"OAuth2 SMTP authentication failed: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup connections"""
        self.exit_server()
        return False

    def exit_server(self):
        """Close all server connections"""
        try:
            if self.sendserver:
                self.sendserver.quit()
        except Exception:
            pass

        try:
            if self.receiveserver:
                self.receiveserver.close()
                self.receiveserver.logout()
        except Exception:
            pass

    def send(self, toaddr: str, subject: str = '', msg: str = '',
             html: bool = False) -> None:
        """
        Send an email.

        Args:
            toaddr: Recipient email address
            subject: Email subject
            msg: Email message body
            html: Whether the message is HTML (default: False for plain text)

        Raises:
            MessageError: If sending fails
        """
        if not self.sendserver:
            raise ConnectionError("SMTP server not connected")

        try:
            email_msg = MIMEMultipart('alternative') if html else MIMEText(msg)
            email_msg['From'] = self.username
            email_msg['To'] = toaddr
            email_msg['Subject'] = subject

            if html:
                part = MIMEText(msg, 'html')
                email_msg.attach(part)

            self.sendserver.sendmail(self.username, toaddr, email_msg.as_string())
        except Exception as e:
            raise MessageError(f"Failed to send email: {e}")

    def filter(self, search_string: str) -> List[Message]:
        """
        Filter emails using Gmail search syntax.

        Args:
            search_string: Gmail-style search string (e.g., 'from:foo@bar.com')

        Returns:
            List of messages matching the search criteria
        """
        if not self.receiveserver:
            raise ConnectionError("IMAP server not connected")

        # Gmail's advanced search is limited by the mailbox selection
        self.receiveserver.select("Inbox")

        try:
            _, data = self.receiveserver.uid('SEARCH', None, 'X-GM-RAW', search_string)

            if not data or not data[0]:
                return []

            fetch_list = data[0].decode().split(' ') if isinstance(data[0], bytes) else data[0].split(' ')
            emails = []

            for email_id in fetch_list:
                if email_id:  # Skip empty strings
                    try:
                        emails.append(self.get_email(email_id))
                    except Exception:
                        continue

            return emails
        except Exception as e:
            raise MessageError(f"Failed to filter emails: {e}")

    def get_all_messages(self) -> List[Message]:
        """
        Get all messages from the inbox.

        Returns:
            List of all inbox messages

        Note:
            This could take a while for large inboxes
        """
        if not self.receiveserver:
            raise ConnectionError("IMAP server not connected")

        self.receiveserver.select('Inbox')

        try:
            _, data = self.receiveserver.search(None, '(UNDELETED)')

            if not data or not data[0]:
                return []

            fetch_list = data[0].decode().split(' ') if isinstance(data[0], bytes) else data[0].split(' ')
            inbox_emails = []

            for email_id in fetch_list:
                if email_id:
                    try:
                        inbox_emails.append(self.get_email(email_id))
                    except Exception:
                        continue

            return inbox_emails
        except Exception as e:
            raise MessageError(f"Failed to get all messages: {e}")

    def unread(self) -> List[Message]:
        """
        Get all unread messages from the inbox.

        Returns:
            List of unread messages
        """
        if not self.receiveserver:
            raise ConnectionError("IMAP server not connected")

        self.receiveserver.select('Inbox')

        try:
            _, data = self.receiveserver.search(None, 'UNSEEN')

            if not data or not data[0]:
                return []

            fetch_list = data[0].decode().split(' ') if isinstance(data[0], bytes) else data[0].split(' ')

            if fetch_list == ['']:
                return []

            unread_emails = []
            for email_id in fetch_list:
                if email_id:
                    try:
                        unread_emails.append(self.get_email(email_id))
                    except Exception:
                        continue

            return unread_emails
        except Exception as e:
            raise MessageError(f"Failed to get unread messages: {e}")

    def get_email(self, email_id: Union[str, bytes]) -> Message:
        """
        Get a specific email by ID.

        Args:
            email_id: Email ID to fetch

        Returns:
            Message object
        """
        if not self.receiveserver:
            raise ConnectionError("IMAP server not connected")

        self.receiveserver.select('Inbox')

        try:
            # Convert email_id to bytes if it's a string
            if isinstance(email_id, str):
                email_id = email_id.encode()

            _, data = self.receiveserver.fetch(email_id, "(RFC822)")
            fetched_email = data[0][1]
            return Message(fetched_email)
        except Exception as e:
            raise MessageError(f"Failed to get email {email_id}: {e}")

    def create_mailbox(self, mailbox: str) -> None:
        """
        Create a new mailbox/label.

        Args:
            mailbox: Name of the mailbox to create
        """
        if not self.receiveserver:
            raise ConnectionError("IMAP server not connected")

        try:
            self.receiveserver.create(mailbox)
        except Exception as e:
            raise MessageError(f"Failed to create mailbox: {e}")

    def append(self, mailbox: str, flags: str, date_time, message: str) -> None:
        """
        Append a message to a mailbox.

        Args:
            mailbox: Target mailbox name
            flags: IMAP flags for the message
            date_time: Date/time for the message
            message: The message content
        """
        if not self.receiveserver:
            raise ConnectionError("IMAP server not connected")

        try:
            self.receiveserver.append(mailbox, flags, date_time, message)
        except Exception as e:
            raise MessageError(f"Failed to append message: {e}")

    def inbox(self, start: int = 0, amount: int = 10) -> List[Message]:
        """
        Get a range of messages from the inbox.

        Args:
            start: Starting position (0-indexed)
            amount: Number of messages to fetch

        Returns:
            List of messages
        """
        if not self.receiveserver:
            raise ConnectionError("IMAP server not connected")

        self.receiveserver.select('Inbox')

        try:
            uids = self._get_uids()
            messages_to_fetch = ','.join(uids[start:start + amount])

            if not messages_to_fetch:
                return []

            _, fetch_list = self.receiveserver.uid('fetch', messages_to_fetch, '(RFC822)')
            inbox_emails = []

            for each_email in fetch_list:
                if isinstance(each_email, tuple) and len(each_email) > 1:
                    inbox_emails.append(Message(each_email[1]))

            return inbox_emails
        except Exception as e:
            raise MessageError(f"Failed to get inbox messages: {e}")

    def get_inbox_count(self) -> int:
        """
        Get the total number of messages in the inbox.

        Returns:
            Number of messages in inbox
        """
        if not self.receiveserver:
            raise ConnectionError("IMAP server not connected")

        try:
            result = self.receiveserver.select('Inbox')
            return int(result[1][0])
        except Exception as e:
            raise MessageError(f"Failed to get inbox count: {e}")

    def _get_uids(self) -> List[str]:
        """
        Get all UIDs from the inbox in reverse order (newest first).

        Returns:
            List of message UIDs
        """
        if not self.receiveserver:
            raise ConnectionError("IMAP server not connected")

        self.receiveserver.select('Inbox')

        try:
            _, data = self.receiveserver.uid('search', None, 'ALL')

            if not data or not data[0]:
                return []

            uids = data[0].decode().split(' ') if isinstance(data[0], bytes) else data[0].split(' ')
            uids.reverse()
            return [uid for uid in uids if uid]  # Filter out empty strings
        except Exception as e:
            raise MessageError(f"Failed to get UIDs: {e}")


# Legacy alias for backwards compatibility
message = Message
account = Account
