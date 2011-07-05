import imaplib
import smtplib
import email

class message:
    def __init__(self, fetched_email):
        accepted_types = ['text/plain']
        parsed = email.message_from_string(fetched_email)
        self.reciever_addr = parsed['to']
        self.sender_addr = parsed['from']
        self.date = parsed['date']
        self.subject = parsed['subject']
        self.body = ''
        if parsed.is_multipart():
            for part in parsed.walk():
                if part.get_content_type() in accepted_types:
                    self.body = part.get_payload()
        else:
            if parsed.get_content_type() in accepted_types:
                self.body = parsed.get_payload()

class account:
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.sendserver = smtplib.SMTP('smtp.gmail.com:587')
        self.sendserver.starttls()
        self.sendserver.login(username,password)

        self.recieveserver = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        self.recieveserver.login(username,password)

    def send(self, toaddr, subject='', msg=''):
        fromaddr = self.username

        headers = ["From: " + fromaddr,
               "Subject: " + subject,
                   "To: " + toaddr,
                   "MIME-Version: 1.0",
                   "Content-Type: text/html"]
        headers = "\r\n".join(headers)
        self.sendserver.sendmail(fromaddr, toaddr, headers + "\r\n\r\n" + msg)

    def recieve(self):
        return

    def inbox(self):
        self.recieveserver.select('Inbox')
        fetch_list = self.recieveserver.search(None, '(UNDELETED)')[1][0]
        fetch_list = fetch_list.split(' ')
        inbox_emails = []
        for each_email in fetch_list:
            inbox_emails.append(self.get_email(each_email))
        return inbox_emails

    def unread(self):
        self.recieveserver.select()
        fetch_list = self.recieveserver.search(None,'UnSeen')[1][0]
        fetch_list = fetch_list.split(' ')
        unread_emails = []
        for each_email in fetch_list:
            unread_emails.append(self.get_email(each_email))
        return unread_emails

    def get_email(self, email_id):
        self.recieveserver.select('Inbox')
        #This nasty syntax fetches the email as a string
        fetched_email = self.recieveserver.fetch(email_id, "(RFC822)")[1][0][1]
        parsed_email = message(fetched_email)
        return parsed_email

    def get_inbox_count(self):
        return int(self.recieveserver.select('Inbox')[1][0])

