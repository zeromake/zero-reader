import smtplib
from email.mime.text import MIMEText
from email.header import Header

_ENCODE = 'utf8'

class Email(object):
    def __init__(self, smtp_host: str, smtp_port: int, account: str, password: str, ssl: int=0):
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._account = account
        self._password = password
        self._ssl = ssl

    def send_email(self, receiver: str, title: str, msg: str):
        status = False
        try:
            message = MIMEText(msg, 'html', _ENCODE)
            message["From"] = self._account
            message["To"] = Header(receiver, _ENCODE)
            message['Subject'] = Header(title, _ENCODE)
            if self._ssl == 1:
                smtpObj = smtplib.SMTP_SSL(self._smtp_host, self._smtp_port)
            else:
                smtpObj = smtplib.SMTP(self._smtp_host, self._smtp_port)
                if self._ssl == 2:
                    smtpObj.docmd("EHLO server" )
                    smtpObj.starttls()
            smtpObj.login(self._account, self._password)
            smtpObj.sendmail(self._account, receiver, message.as_string())
            smtpObj.quit()
            status = True
        except Exception as e:
            print(e)
        return status
    

