# Python Gmail Library

A modern Python 3 library for interacting with Gmail using IMAP and SMTP protocols.

## Features

- **Python 3.8+** - Fully modernized for Python 3
- **Type hints** - Complete type annotations for better IDE support
- **OAuth2 support** - Secure authentication using OAuth2 tokens
- **Context managers** - Automatic resource cleanup
- **Error handling** - Specific exceptions for different error types
- **Modern email API** - Uses the latest email.policy for better RFC compliance
- **Gmail search** - Support for Gmail's advanced search syntax

## Installation

### Using pip (recommended)

```bash
pip install gmaillib
```

### From source

```bash
git clone https://github.com/thedjpetersen/gmaillib.git
cd gmaillib
pip install -e .
```

## Quick Start

### Basic Authentication (Password)

```python
import gmaillib

# Initialize account with password
account = gmaillib.Account('your-email@gmail.com', password='your-password')

# Get inbox messages
messages = account.inbox()
for msg in messages:
    print(f"From: {msg.sender_addr}")
    print(f"Subject: {msg.subject}")

# Clean up
account.exit_server()
```

### Using Context Managers (Recommended)

```python
import gmaillib

# Automatic cleanup with context manager
with gmaillib.Account('your-email@gmail.com', password='your-password') as account:
    messages = account.inbox()
    for msg in messages:
        print(f"From: {msg.sender_addr}")
```

### OAuth2 Authentication (Recommended for Production)

```python
import gmaillib

# Initialize with OAuth2 token
account = gmaillib.Account(
    'your-email@gmail.com',
    oauth2_token='your-oauth2-access-token'
)

messages = account.unread()
account.exit_server()
```

## Usage Examples

### Reading Emails

#### Get a range of messages

```python
with gmaillib.Account('email@gmail.com', password='pass') as account:
    # Get 10 messages starting from position 0
    messages = account.inbox(start=0, amount=10)

    # Get next 10 messages
    messages = account.inbox(start=10, amount=10)
```

#### Get all unread messages

```python
with gmaillib.Account('email@gmail.com', password='pass') as account:
    unread = account.unread()
    print(f"You have {len(unread)} unread messages")
```

#### Get inbox count

```python
with gmaillib.Account('email@gmail.com', password='pass') as account:
    count = account.get_inbox_count()
    print(f"Total messages: {count}")
```

#### Get all messages (warning: may be slow for large inboxes)

```python
with gmaillib.Account('email@gmail.com', password='pass') as account:
    all_messages = account.get_all_messages()
```

### Searching Emails

Use Gmail's advanced search syntax:

```python
with gmaillib.Account('email@gmail.com', password='pass') as account:
    # Search by sender
    messages = account.filter('from:someone@example.com')

    # Search by subject
    messages = account.filter('subject:important')

    # Complex search
    messages = account.filter('from:boss@company.com subject:urgent after:2024/01/01')

    # Search with labels
    messages = account.filter('label:work is:unread')
```

### Sending Emails

#### Send plain text email

```python
with gmaillib.Account('email@gmail.com', password='pass') as account:
    account.send(
        toaddr='recipient@example.com',
        subject='Hello',
        msg='This is a plain text message'
    )
```

#### Send HTML email

```python
with gmaillib.Account('email@gmail.com', password='pass') as account:
    html_content = '''
    <html>
        <body>
            <h1>Hello!</h1>
            <p>This is an <strong>HTML</strong> email.</p>
        </body>
    </html>
    '''
    account.send(
        toaddr='recipient@example.com',
        subject='HTML Email',
        msg=html_content,
        html=True
    )
```

### Working with Attachments

```python
with gmaillib.Account('email@gmail.com', password='pass') as account:
    messages = account.inbox(amount=5)

    for msg in messages:
        # Download attachments to a directory
        result = msg.download_attachment('/path/to/save/directory')
        print(result)
```

### Working with Message Content

```python
with gmaillib.Account('email@gmail.com', password='pass') as account:
    messages = account.inbox(amount=1)
    msg = messages[0]

    # Access message properties
    print(f"From: {msg.sender_addr}")
    print(f"To: {msg.receiver_addr}")
    print(f"Date: {msg.date}")
    print(f"Subject: {msg.subject}")
    print(f"Body: {msg.body}")

    # Get HTML content
    html_messages = gmaillib.Message(msg.parsed_email, types=['text/html'])
    print(html_messages.body)
```

### Error Handling

```python
import gmaillib
from gmaillib import AuthenticationError, ConnectionError, MessageError

try:
    with gmaillib.Account('email@gmail.com', password='wrong-password') as account:
        messages = account.inbox()
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except MessageError as e:
    print(f"Message operation failed: {e}")
```

### Advanced: Managing Mailboxes

```python
with gmaillib.Account('email@gmail.com', password='pass') as account:
    # Create a new mailbox/label
    account.create_mailbox('MyNewLabel')

    # Append a message to a mailbox
    account.append(
        mailbox='MyNewLabel',
        flags='\\Seen',
        date_time=None,
        message='email content here'
    )
```

## API Reference

### Account Class

#### `Account(username, password=None, oauth2_token=None)`

Initialize a Gmail account connection.

**Parameters:**
- `username` (str): Gmail email address
- `password` (str, optional): Account password for basic auth
- `oauth2_token` (str, optional): OAuth2 access token (recommended)

**Raises:**
- `AuthenticationError`: If authentication fails
- `ConnectionError`: If connection to Gmail servers fails

#### Methods

- `inbox(start=0, amount=10)` - Get a range of inbox messages
- `unread()` - Get all unread messages
- `get_all_messages()` - Get all inbox messages
- `get_inbox_count()` - Get total number of inbox messages
- `send(toaddr, subject='', msg='', html=False)` - Send an email
- `filter(search_string)` - Search emails using Gmail syntax
- `create_mailbox(mailbox)` - Create a new mailbox/label
- `append(mailbox, flags, date_time, message)` - Append message to mailbox
- `exit_server()` - Close all connections

### Message Class

#### `Message(fetched_email, **kwargs)`

Represents an email message.

**Parameters:**
- `fetched_email` (str or bytes): Raw email data
- `types` (list, optional): Acceptable content types (default: ['text/plain'])

#### Attributes

- `parsed_email` - The parsed email message object
- `receiver_addr` - Email address of the receiver
- `sender_addr` - Email address of the sender
- `date` - Date the message was sent
- `subject` - Subject of the email
- `body` - Content of the email

#### Methods

- `download_attachment(dest_dir)` - Download attachments to directory

## Migration from Old Version

If you're upgrading from the Python 2 version, here are the key changes:

### Code Changes

```python
# Old (Python 2)
import gmaillib
account = gmaillib.account('email', 'pass')  # lowercase 'account'

# New (Python 3)
import gmaillib
account = gmaillib.Account('email', password='pass')  # capitalized, keyword args
```

### Backwards Compatibility

For minimal code changes, lowercase aliases are available:

```python
import gmaillib
account = gmaillib.account('email', 'pass')  # Still works!
msg = gmaillib.message(email_data)  # Still works!
```

### Major Improvements

1. **Print statements** → `print()` functions
2. **String handling** - Proper bytes/str handling for Python 3
3. **Email parsing** - Uses modern `email.policy.default`
4. **Context managers** - Use `with` statements for auto cleanup
5. **Type hints** - Better IDE support and code documentation
6. **OAuth2** - Secure authentication support
7. **Error handling** - Specific exception types

## Requirements

- Python 3.8 or higher
- No external dependencies (uses stdlib only)

## Security Notes

### App Passwords

If using password authentication with 2FA enabled, you'll need to generate an [App Password](https://support.google.com/accounts/answer/185833):

1. Go to your Google Account
2. Select Security
3. Under "Signing in to Google," select App Passwords
4. Generate a new app password for "Mail"
5. Use this password instead of your regular password

### OAuth2 (Recommended)

For production applications, use OAuth2 authentication:

1. Set up a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Gmail API
3. Create OAuth2 credentials
4. Get an access token
5. Pass the token to `Account(oauth2_token=...)`

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=gmaillib
```

### Code Quality

```bash
# Format code
black gmaillib.py

# Lint code
ruff check gmaillib.py

# Type checking
mypy gmaillib.py
```

## License

MIT License - Copyright (c) 2013-2024 David Petersen

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Credits

- Original library by David Petersen
- Inspired by [this excellent blog post](http://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/)
- Contributors: See GitHub contributors page

## Changelog

### Version 1.0.0 (2024)

- **Breaking**: Python 3.8+ required (dropped Python 2 support)
- **New**: OAuth2 authentication support
- **New**: Context manager support
- **New**: Type hints throughout
- **New**: Specific exception types
- **Improved**: Modern email parsing with email.policy
- **Improved**: Better bytes/string handling
- **Improved**: HTML email support in send()
- **Improved**: Better error messages
- **Fixed**: All Python 3 compatibility issues

### Version 0.0.0 (2013)

- Initial release
- Python 2 support
- Basic IMAP/SMTP functionality
