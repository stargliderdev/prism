#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

import nexmo


def send_sms(text_message, number):
    responce = {}
    to_number = '00351' + str(number)
    client = nexmo.Client(key='a405aef8', secret='95bddad3')
    sd = client.send_message({'from': 'Espiridiao', 'to': to_number, 'text': text_message, 'type': 'unicode'})
    # print('TO_NUMBER', to_number, type(to_number))
    # print(sd)
    # print(sd['messages'])
    foo = sd['messages'][0]
    responce['status'] = int(foo['status'])
   
    if responce['status'] == 0:
        responce['saldo'] = '{0:2.4f}'.format(float(foo['remaining-balance']))
        responce['custo'] = foo['message-price']
        responce['return_msg'] = 'Saldo:' + '{0:2.4f}'.format(float(foo['remaining-balance']))
    else:
        responce['saldo'] = '0'
        responce['custo'] = '0'
        responce['return_msg'] = foo['error-text']
    return responce

def send_mail(data_dict): # to_list, msg_headers, att_files):
    flag = False
    smtpserver = 'hosting15.serverhs.org'
    AUTHREQUIRED = 0 # if you need to use SMTP AUTH set to 1
    smtpuser = 'saft@jheg.pt'
    smtppass = 'D*F,5N$w2u4)'
    msg = MIMEMultipart()
    msg['Subject'] = data_dict['sub'] # msg_headers['sub']  #SUBJECT
    msg['From'] = data_dict['from'] #'saft@jheg.pt'
    to_list = data_dict['send_to']
    msg['To'] = ','.join(to_list)
    text_body = data_dict['body']
    att_files = data_dict['att_files']
    part1 = MIMEText(text_body, 'html', 'UTF-8')
    msg.attach(part1)
    for n in att_files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(n, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(n))
        msg.attach(part)

    session = smtplib.SMTP(smtpserver,25)
    session.ehlo()
    session.starttls()
    session.ehlo()
    session.login(smtpuser, smtppass)
    smtpresult = session.sendmail('saft@jheg.pt', to_list, msg.as_string())
    if smtpresult:
        errstr = ""
        for recip in list(smtpresult.keys()):
            errstr = """Could not delivery mail to: %s
                Server said: %s
                %s
                %s""" % (recip, smtpresult[recip][0], smtpresult[recip][1], errstr)
        raise smtplib.SMTPException(errstr)
        return False
    else:
        return True


if __name__ == "__main__":
    send_mail({'send_to': ['xeo@net.vodafone.pt','comercial@espiridiao.pt', 'suporte@espiridiao.pt'],
               'sub': 'teste v3',
               'from': 'saft@jheg.pt',
               'body': 'bla bla bla',
               'att_files': ['logos.ico', 'logos6.spec']})