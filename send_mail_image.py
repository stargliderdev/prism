import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText  # Added
from email.mime.image import MIMEImage

smtpserver = 'mail.espiridiao.net'
AUTHREQUIRED = 0  # if you need to use SMTP AUTH set to 1
smtpuser = 'assistencias@espiridiao.net'
smtppass = 'QEF!tp;7!3wh'
SUBJECT = '\u27A4 teste'  # msg_headers['sub']

attachment = 'move.png'
to = 'gerencia@espiridiao.pt'
msg = MIMEMultipart()
msg["To"] = to
msg["From"] = 'assistencias@espiridiao.net'
msg["Subject"] = SUBJECT
body = 'the quick and dirty brown foxx'
msgText = MIMEText('<b>%s</b><br><img src="cid:%s"><br>' % (body, attachment), 'html')
msg.attach(msgText)   # Added, and edited the previous line

fp = open(attachment, 'rb')
img = MIMEImage(fp.read())
fp.close()
img.add_header('Content-ID', '<{}>'.format(attachment))
msg.attach(img)

# print (msg.as_string())

session = smtplib.SMTP(smtpserver, 25)
session.ehlo()
session.starttls()
session.ehlo()
flag = (True,'')
try:
    session.login(smtpuser, smtppass)
    smtpresult = session.sendmail('assistencias@espiridiao.net', to, msg.as_string())
except Exception as e:
    flag = (False, str(e))

print(flag)

exit(0)


