Python module for GMail
===

Simple Python module to interact with Google's mail service GMail. The module
uses Python's included imaplib and smtplib for recieving and sending emails.

The goal of this module is to provide a simple direct interface to GMail.

Usage
---

To initialize an account you do the following

    import gmaillib

    account = gmaillib.account('username', 'password')

To get the entire contents of the inbox

	account.get_all_messages()

To only get the unread messages of the inbox

	account.unread();

To send an email

	account.send(target, subject, message)

Note that the subject and message are optional.
