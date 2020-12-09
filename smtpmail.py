#!/usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
# from email import Encoders
# from email.MIMEBase import MIMEBase
import data_sets
import html_maker
import liblogos
import stdio
import libpg
import parameters as pa


def send_mail_html_v1(SUBJECT, BODY, TO, FROM, FORMAT = 'html'):
    MESSAGE = MIMEMultipart('alternative')
    MESSAGE['subject'] = SUBJECT
    MESSAGE['To'] = ','.join(TO)       # TO
    MESSAGE['From'] = FROM
    MESSAGE.preamble = """
Your mail reader does not support the report format.
Please visit us <a href="http://www.mysite.com">online</a>!"""
    HTML_BODY = MIMEText(BODY, FORMAT,'UTF-8')
    MESSAGE.attach(HTML_BODY)
    server = smtplib.SMTP('www.espiridiao.pt')
    if __name__ == "__main__":
        server.set_debuglevel(1)
    password = "1697fo"
    server.starttls()
    server.login(FROM,password)
    server.sendmail(FROM,TO, MESSAGE.as_string())
    server.quit()


def send_mail_html(to,msg_headers):
    smtpserver = 'mail.espiridiao.net'
    AUTHREQUIRED = 0 # if you need to use SMTP AUTH set to 1
    smtpuser = 'assistencias@espiridiao.net'
    smtppass = 'QEF!tp;7!3wh'
    SUBJECT = msg_headers['sub']

    msg = MIMEMultipart()
    msg['Subject'] = SUBJECT
    msg['From'] = 'assistencias@espiridiao.net'
    # msg['From'] = 'noreplay@espiridiao.pt'
    a = libpg.query_one('SELECT ct_value2 from contacts where ct_unit = %s', (pa.unidade_id,) )
    if a is not None:
        to.append(a[0])
    msg['To'] = ','.join(to)
    text = msg_headers['body']
    part1 = MIMEText(text, 'html','UTF-8')
    msg.attach(part1)
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
    return flag


def send_sms_mail(msg_headers):
    to = 'assistencias@espiridiao.net'
    smtpserver = 'mail.espiridiao.net'
    AUTHREQUIRED = 0 # if you need to use SMTP AUTH set to 1
    smtpuser = 'assistencias@espiridiao.net'
    smtppass = 'QEF!tp;7!3wh'
    SUBJECT = msg_headers['sub']

    msg = MIMEMultipart()
    msg['Subject'] = SUBJECT
    msg['From'] = 'assistencias@espiridiao.net'
    msg['To'] = to
    text = msg_headers['body']
    part1 = MIMEText(text, 'html','UTF-8')
    msg.attach(part1)
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
    return flag


def send_mail_lic_order(to, msg_headers):
    smtpserver = 'www.espiridiao.pt'
    AUTHREQUIRED = 0
    smtpuser = 'restware@espiridiao.net'
    smtppass = '9S?&[C^7O=fF'
    SUBJECT = msg_headers['sub']

    msg = MIMEMultipart()
    msg['Subject'] = SUBJECT
    msg['From'] = 'restware@espiridiao.net'
    msg['To'] = 'restware@espiridiao.net'
    text = msg_headers['body']

    part1 = MIMEText(text, 'html','UTF-8')
    msg.attach(part1)
    session = smtplib.SMTP(smtpserver,587)
    session.ehlo()
    session.starttls()
    session.ehlo()
    session.login(smtpuser, smtppass)
    smtpresult = session.sendmail('restware@espiridiao.net', to, msg.as_string())
    if smtpresult:
        errstr = ""
        for recip in list(smtpresult.keys()):
            errstr = """Could not delivery mail to: %s
                Server said: %s
                %s
                %s""" % (recip, smtpresult[recip][0], smtpresult[recip][1], errstr)
            stdio.log_write('./var/log.txt', errstr)
            return False, errstr
    else:
        return True, 'OK'


def upload_lic_mail(order_num, unid_dict):
    """LOAD"""
    subject = '⏫ LOAD-' + str(order_num).zfill(5) + '-' + unid_dict['cl_nif'] + '-' + unid_dict['un_name']
    body = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8"></head><pre>'''
    body += 'Origem: ' + str(order_num) + '<br>'
    body += unid_dict['un_name'] + '<br>'
    body += unid_dict['un_morada'] + '<br>'
    body += unid_dict['un_localidade'] + '<br>'
    body += unid_dict['un_cp'] + '<br>'
    body += pa.user_dict['user_name'] + ' @' + datetime.datetime.now().strftime(' %m.%b.%Y %H:%M')
    body += '</html>'
    msg_headers = {'sub': subject,'body': body}
    smtpserver = 'www.espiridiao.pt'
    AUTHREQUIRED = 0
    smtpuser = 'restware@espiridiao.net'
    smtppass = '9S?&[C^7O=fF'
    SUBJECT = msg_headers['sub']
    msg = MIMEMultipart()
    msg['Subject'] = SUBJECT
    msg['From'] = 'restware@espiridiao.net'
    msg['To'] = 'assistencias@espiridiao.net'
    text = msg_headers['body']

    part1 = MIMEText(text, 'html', 'UTF-8')
    msg.attach(part1)
    session = smtplib.SMTP(smtpserver, 587)
    session.ehlo()
    session.starttls()
    session.ehlo()
    session.login(smtpuser, smtppass)
    smtpresult = session.sendmail('restware@espiridiao.net', 'assistencias@espiridiao.net', msg.as_string())
    if smtpresult:
        errstr = ""
        for recip in list(smtpresult.keys()):
            errstr = """Could not delivery mail to: %s
                    Server said: %s
                    %s
                    %s""" % (recip, smtpresult[recip][0], smtpresult[recip][1], errstr)
            stdio.log_write('./var/log.txt', errstr)
            # raise smtplib.SMTPException, errstr
            return False, errstr
    else:
        return True, 'OK'
  

def send_process_mail(process_id):   
    process_dict = data_sets.process_to_dict(process_id)
    msg_body = html_maker.process_to_html(process_dict)
    if process_dict['proc_pendente']:
        assunto = '❌ [' + process_dict['proc_type'] + '] ' + process_dict['proc_unit_name']
    else:
        if process_dict['proc_type'] == 'INFO':
            assunto = '🔔 [' + process_dict['proc_type'] + '] ' + process_dict['proc_unit_name']
        else:
            assunto = '✅ [' + process_dict['proc_type'] + '] ' + process_dict['proc_unit_name']
    """ envia internamente """
    if pa.DEVELOP:
        mailing_list = ['xeo@net.vodafone.pt']
    else:
        mailing_list = ['assistencias@espiridiao.net']
    
    hl = liblogos.get_sys_admin(process_dict['proc_unit_id'])
    if hl[0]:
        mailing_list.append(hl[2])
    msg_dic = {'sub': assunto,'body': msg_body}
    send_mail_html(mailing_list, msg_dic)


def SEND_BLOCK_MAIL(process_id, order_id, data):
    process_dict = data_sets.process_to_dict(process_id)
    msg_body = html_maker.block_to_html(process_dict)
    
    if order_id == 1:
        assunto = 'BLOQUEADO ' + process_dict['proc_unit_name'] + ' até ' + data
    elif order_id == 2:
        assunto = 'DESBLOQUEADO ' + process_dict['proc_unit_name'] + ' Pago'
    elif order_id == 3:
        assunto = '🔴 BLOQUEAR ' + process_dict['proc_unit_name'] + ' para ' + data
    elif order_id == 4:
        assunto = '🔴 DESBLOQUEAR ' + process_dict['proc_unit_name'] + ' Tudo pago'
    """ envia internamente """
    if pa.DEVELOP:
        mailing_list = ['xeo@net.vodafone.pt']
    else:
        mailing_list = ['assistencias@espiridiao.net']
    
    hl = liblogos.get_sys_admin(process_dict['proc_unit_id'])
    if hl[0]:
        mailing_list.append(hl[2])
    msg_dic = {'sub': assunto, 'body': msg_body}
    send_mail_html(mailing_list, msg_dic)

  
  
if __name__ == '__main__':
    pass
