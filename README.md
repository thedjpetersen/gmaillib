Python module for GMail
===

Simple Python module to interact with Google's mail service GMail. The module
uses Python's included imaplib and smtplib for recieving and sending emails.

Usage
---

To initialize an account you do the following

    import gmaillib

    account = gmaillib.account('username', 'password')
