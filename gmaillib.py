import imaplib
import smtplib
import email
import os

class message:
    def __init__(self, fetched_email):
        accepted_types = ['text/plain']
        parsed = email.message_from_string(fetched_email)
        self.parsed_email = email.message_from_string(fetched_email)
        self.receiver_addr = parsed['to']
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

    def __repr__(self):
        return "<Msg from: {0}>".format(self.sender_addr)

    def __str__(self):
        return "To: {0}\nFrom: {1}\nDate: {2}\nSubject: {3}\n\n{4}".format(
            self.receiver_addr, self.sender_addr, self.date, self.subject, self.body)

    def download_attachment(self, dest_dir):
        '''
        Courtsey of http://stackoverflow.com/questions/348630/how-can-i-download-all-emails-with-attachments-from-gmail
        '''
        mail = self.parsed_email
        if mail.get_content_maintype() != 'multipart':
            return "no attachment"

        print "["+ mail["From"]+"] :" + mail["Subject"]

        for part in mail.walk():
            if part.get_content_maintype() == 'multipart':
                continue
 
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            counter = 1

            if not filename:
                filename = 'part-%03d%s' % (counter, 'bin')
                counter += 1

            att_path = os.path.join(dest_dir, filename)

            if not os.path.isfile(att_path) :
                fp = open(att_path, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()

class account:
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.sendserver = smtplib.SMTP('smtp.gmail.com:587')
        self.sendserver.starttls()
        self.sendserver.login(username,password)

        self.receiveserver = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        self.receiveserver.login(username,password)

    def send(self, toaddr, subject='', msg=''):
        fromaddr = self.username

        headers = ["From: " + fromaddr,
               "Subject: " + subject,
                   "To: " + toaddr,
                   "MIME-Version: 1.0",
                   "Content-Type: text/html"]
        headers = "\r\n".join(headers)
        self.sendserver.sendmail(fromaddr, toaddr, headers + "\r\n\r\n" + msg)

    def receive(self):
        return

    def filter(self, search_string):
        '''
        This function provides gmail style search.

        @type search_string: string
        @param search_string: GMail style search string

        @return list of email matching the search criteria
        
        '''
        
        # NOTE: Gmail's advanced search is limited by the mail box selection
        # irrespective of what we include in the search string.
        # e.g. label:anywhere will return Inbox results only.

        self.receiveserver.select("Inbox")
        fetch_str = self.receiveserver.uid('SEARCH', None, 'X-GM-RAW', search_string)[1][0]
        fetch_list = fetch_str.split(' ')
        emails = []
        for email_index in fetch_list:
            emails.append(self.get_email(email_index))
        return emails

    def get_all_messages(self):
        self.receiveserver.select('Inbox')
        fetch_list = self.receiveserver.search(None, '(UNDELETED)')[1][0]
        fetch_list = fetch_list.split(' ')
        inbox_emails = []
        for each_email in fetch_list:
            inbox_emails.append(self.get_email(each_email))
        return inbox_emails

    def unread(self):
        self.receiveserver.select('Inbox')
        fetch_list = self.receiveserver.search(None,'UnSeen')[1][0]
        fetch_list = fetch_list.split(' ')
        if fetch_list == ['']:
            return []
        unread_emails = []
        for each_email in fetch_list:
            unread_emails.append(self.get_email(each_email))
        return unread_emails

    def get_email(self, email_id):
        self.receiveserver.select('Inbox')
        #This nasty syntax fetches the email as a string
        fetched_email = self.receiveserver.fetch(email_id, "(RFC822)")[1][0][1]
        parsed_email = message(fetched_email)
        return parsed_email

    def inbox(self, start=0, amount=10):
        self.receiveserver.select('Inbox')
        inbox_emails = []
        messages_to_fetch = ','.join(self._get_uids()[start:start+amount])
        fetch_list = self.receiveserver.uid('fetch', messages_to_fetch,'(RFC822)')
        for each_email in fetch_list[1]:
            if(len(each_email) == 1):
                continue
            inbox_emails.append(message(each_email[1]))
        return inbox_emails

    def get_inbox_count(self):
        return int(self.receiveserver.select('Inbox')[1][0])

    def _get_uids(self):
        self.receiveserver.select('Inbox')
        result, data = self.receiveserver.uid('search', None, 'ALL')
        data = data[0].split(' ')
        data.reverse()
        return data
