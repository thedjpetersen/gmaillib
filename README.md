Python module for GMail
===

Simple Python module to interact with Google's mail service GMail. The module
uses Python's included imaplib and smtplib for recieving and sending emails.

The goal of this module is to provide a simple direct interface to GMail.

This repo includes the Windows installer.(.exe)

Usage
---

To initialize an account you do the following

    import gmaillib

    account = gmaillib.account('username', 'password')

To get messages from the inbox just call the use the inbox method

    account.inbox()

To get a range of messages just give the place to start from and how many to fetch

    account.inbox(start=10, amount=100)

This will fetch the 10th to the 110th message

To get the entire contents of the inbox(**note if you have a large inbox this could take a while**)

	account.get_all_messages()

You can also just get the number of messages in the inbox which is less time consuming.
	
	account.get_inbox_count()

To only get the unread messages of the inbox

	account.unread();

To get messages from the sent just call the use the sent method

	account.sent()

To get a range of messages just give the place to start from and how many to fetch
	
	account.sent(start=10, amount=100)	

To send an email

	account.send(target, subject, message)

Note that the subject and message are optional.


To fetch emails with gmail search syntax. Added support for gmails web search syntax using X-GM-RAW. 

	account.filter('from:foo@bar.com')

Note that, the mailbox selection is set to Inbox(default). https://github.com/shredder12/gmaillib/blob/master/gmaillib.py#L65

Download messages by using download_attachment()
    
    message.download_attachment(location)

Credits
===

A large part of this library is implementing this excellent blogpost: http://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/

License
===

The MIT License (MIT)

Copyright (c) 2013 David Petersen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
