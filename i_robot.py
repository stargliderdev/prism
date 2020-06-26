#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import psycopg2
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import Encoders
from email.MIMEBase import MIMEBase
import stdio
import os


def query_many(sql,data):
    try:
        conn = psycopg2.connect('host=192.168.0.98 dbname=prism user=root password=masterkey')
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        a = cur.fetchall()
        cur.close()
        conn.close()
        return a
    except Exception, e:
        print str(e)
        sys.exit(25)
        

def execute_query(sql, data=(True,)):
    try:
        conn = psycopg2.connect('host=192.168.0.98 dbname=prism user=root password=masterkey')
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        conn.commit()
        cur.close()
        conn.close()
    except Exception,e:
        print ('SQL Execute SQL Error', str(e), sql, data)
        sys.exit(45)


def query_one(sql, data):
    try:
        conn = psycopg2.connect(pa.conn_string)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        cur.close()
        conn.close()
        return cur.fetchone()
    except Exception, e:
        print ((str(e) + '\n -- SQL Error --\n in :' + _mod + '\n' + sql))
        exit(59)


def send_mail(to, filename, msg_headers):
    smtpserver = 'mail.espiridiao.net'
    # smtpserver = base64.b64decode('c210cC5nbWFpbC5jb20=')
    AUTHREQUIRED = 0 # if you need to use SMTP AUTH set to 1
    smtpuser = 'assistencias@espiridiao.net'
    smtppass = 'QEF!tp;7!3wh'
    # smtppass = base64.b64decode('MTY5N2Zvc2FmLXQ=')
    SUBJECT = msg_headers['sub']

    msg = MIMEMultipart()
    msg['Subject'] = SUBJECT
    msg['From'] = 'assistencias@espiridiao.net'
    msg['To'] = ','.join(to)
    text = msg_headers['body']

    part1 = MIMEText(text, 'html','UTF-8')
    # part1 = MIMEText(text, 'html')

    # permite varios ficheiros
    msg.attach(part1)
    for n in filename:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(n, "rb").read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(n))
        msg.attach(part)
    session = smtplib.SMTP(smtpserver,25)
    session.ehlo()
    session.starttls()
    session.ehlo()
    #if AUTHREQUIRED:
    session.login(smtpuser, smtppass)
    smtpresult = session.sendmail('assistencias@espiridiao.net', to, msg.as_string())

    if smtpresult:
        errstr = ""
        for recip in smtpresult.keys():
            errstr = """Could not delivery mail to: %s
                Server said: %s
                %s
                %s""" % (recip, smtpresult[recip][0], smtpresult[recip][1], errstr)
            stdio.log_write('./log.txt', errstr)
        raise smtplib.SMTPException, errstr
    # stdio.log_write('./var/log.txt','Mail send!')


def assistencias_pendentes():
    sql = '''SELECT proc_id, to_char(proc_date, 'DD.MON.YYYY') , unidades.un_name, proc_tags,proc_status, proc_unit_id,
              (date  'today' - assistencias.proc_date::timestamp::date) as days_delay
            from assistencias,unidades
            where assistencias.proc_pendente = True and unidades.un_id= assistencias.proc_unit_id
            order by proc_date desc'''
    pendentes = query_many(sql, (True,))
    html =  ''''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8"><title>Relatorio</title>''' + '<style>' + CSS1 + '</style>'
    html += '''<table width="900" align="center">\n'''
    stack = -1
    for n in pendentes:
        if stack <> n[6]:
            if n[6] == 0:
                foo = '''<tr class="cores">\n<td id="linha2" nowrap="" align="left" colspan="8">Hoje</td></tr>\n'''
            elif n[6] == 1:
                foo = '''<tr class="cores">\n<td id="linha2" nowrap="" align="left" colspan="8">Ontem</td></tr>\n'''
            elif n[6] >= 2:
               foo = '''<tr class="cores">\n<td id="linha2" nowrap="" align="left" colspan="8">''' +  str(n[6]) + ' dias da atraso.</td></tr>\n'
            #print 'assistencias ', foo
            html += foo
            html +='''<tr class="cores"><td id="linha_encP" align="right">''' + str(n[0]) + '</td><td id="linha_encP" align="center">' + n[1] +\
                   '</td><td id="linha_encP" align="left">' + n[2] + \
                   '</td><td id="linha_encP" align="left">' + n[3] + \
                   '</td><td id="linha_encP" align="left">' + n[4] + \
                   '</td></tr>\n'
            stack = n[6]
        else:
            html +='''<tr class="cores"><td id="linha_encP" align="right">''' + str(n[0]) + '</td><td id="linha_encP" align="center">' + n[1] +\
                   '</td><td id="linha_encP" align="left">' + n[2] + \
                   '</td><td id="linha_encP" align="left">' + n[3] + \
                   '</td><td id="linha_encP" align="left">' + n[4] + \
                   '</td></tr>\n'
    html += '</table></html>'
    send_mail_html('Assistencias pendentes @ ' + datetime.datetime.now().strftime("%a, %d %b %Y"), html ,['assistencias@espiridiao.net'],'assistencias@espiridiao.net')


def call_center_to_end(days=10,back_days=-10):
    html = CSS
    html += '''
        <table width="900" align="center">
        <th id="cabecalho" width="100"># Un</th>
        <th id="cabecalho" width="400">Unidade</th>
        <th id="cabecalho" width="200">Fim</th>

        <th id="cabecalho" width="300">Valido</th>
        '''
    sql = '''SELECT cm_unit_id, unidades.un_name,
         comitments_unit.cm_value
        ,(to_date(comitments_unit.cm_value, 'YYYY-MM-DD') - DATE 'now') as s
        FROM comitments_unit,unidades
        WHERE  comitments_unit.cm_act_id=15 and cm_archive = False
        and ( to_date(comitments_unit.cm_value, 'YYYY-MM-DD') - DATE 'now'  <= %s
        and to_date(comitments_unit.cm_value, 'YYYY-MM-DD') - DATE 'now' >=%s)
        and unidades.un_id= comitments_unit.cm_unit_id and un_activa=True
        order by s asc'''
    warn = query_many(sql, (days,back_days))
    if len(warn) > 0:
        for n in warn:
            html += '''<tr class="cores">'''
            html += '''<td id="linha_encP" align="right">''' + str(n[0]) + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + str(n[1]) + '</td>\n'
            html += '''<td id="linha_encP" align="center">''' + str(n[2]) + '</td>\n'
            html += '''<td id="linha_encP" align="right">''' + str(n[3]) + '</td>\n'
            html += '</tr>\n'
        html += '</table>'
    msg_dic = {'sub': u'Call Center e terminar em ' + str(days) + ' dias em ' + datetime.datetime.now().strftime("%d %b %Y"), 'body': html}
    send_mail(['gerencia@espiridiao.pt','escritorio@espiridiao.net','toze@espiridiao.net'], [], msg_dic)


def software_expire_date(days=30):
    html = CSS
    html += '''
        <table width="600" align="center">
        <th id="cabecalho" width="80" ># UN</th>
        <th id="cabecalho" width="400">Unidade</th>
        <th id="cabecalho" width="150">Valido</th>
        <th id="cabecalho" width="80">Dias</th>
        '''
    sql = '''SELECT cm_unit_id, unidades.un_name,
         comitments_unit.cm_value
        ,(to_date(comitments_unit.cm_value, 'YYYY-MM-DD') - DATE 'now') as s
        FROM comitments_unit,unidades
        WHERE  comitments_unit.cm_act_id=14 and cm_archive = False
        and ( to_date(comitments_unit.cm_value, 'YYYY-MM-DD') - DATE 'now'  <= %s
        and to_date(comitments_unit.cm_value, 'YYYY-MM-DD') - DATE 'now' >=1)
        and unidades.un_id= comitments_unit.cm_unit_id and un_activa=True
        order by s asc'''
    dataset = query_many(sql, (days,))
    
    if len(dataset) > 0:
        for n in dataset:
            html += '''<tr class="cores">'''
            html += '''<td id="linha_encP" align="right">''' + str(n[0]) + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + n[1] + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + str(n[2]) + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + str(n[3]) + '</td>\n'
            # html += '''<td id="linha_encP" align="left">''' + str(n[5]) + '</td>\n'
            # html += '''<td id="linha_encP" align="right">''' + str(n[6]) + '</td>\n'
            html += '</tr>\n'
        html += '</table>'
        msg_dic = {'sub': u'Software a terminar até 30 dias em ' + datetime.datetime.now().strftime("%d %b %Y"), 'body': html}
        send_mail(['gerencia@espiridiao.pt','escritorio@espiridiao.net','toze@espiridiao.net'], [], msg_dic)


def software_block_date(days=1, back_days=-8):
    html = CSS
    html += '''
        <table width="600" align="center">
        <th id="cabecalho" width="100" ># UN</th>
        <th id="cabecalho" width="400">Unidade</th>
        <th id="cabecalho" width="150">Bloqueia</th>
        <th id="cabecalho" width="80">Dias</th>
        '''
    sql = '''SELECT cm_unit_id, unidades.un_name,
         comitments_unit.cm_value
        ,(to_date(comitments_unit.cm_value, 'YYYY-MM-DD') - DATE 'now') as s
        FROM comitments_unit,unidades
        WHERE  comitments_unit.cm_act_id=14 and cm_archive = False
        and ( to_date(comitments_unit.cm_value, 'YYYY-MM-DD') - DATE 'now'  <= %s
        and to_date(comitments_unit.cm_value, 'YYYY-MM-DD') - DATE 'now' >=%s)
        and unidades.un_id= comitments_unit.cm_unit_id and un_activa=True
        order by s asc'''
    dataset = query_many(sql, (days, back_days))
    if len(dataset) > 0:
        for n in dataset:
            html += '''<tr class="cores">'''
            html += '''<td id="linha_encP" align="right">''' + str(n[0]) + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + n[1] + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + str(n[2]) + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + str(n[3]) + '</td>\n'
            # html += '''<td id="linha_encP" align="left">''' + str(n[5]) + '</td>\n'
            # html += '''<td id="linha_encP" align="right">''' + str(n[6]) + '</td>\n'
            html += '</tr>\n'
        html += '</table>'

        msg_dic = {'sub': u'Software a bloquear hoje ' + datetime.datetime.now().strftime("%d %b %Y"), 'body': html}
        send_mail(['gerencia@espiridiao.pt', 'escritorio@espiridiao.net','toze@espiridiao.net'], [], msg_dic)
    
def updater():
    import uuid
    xl = query_many('select un_id from unidades', (True,))
    for n in xl:
        print 'n:', n
        c = str(uuid.uuid4())
        execute_query('update unidades set un_uuid=%s where un_id=%s', (c, n[0]))
        
        
def on_invoice_charge():
    html = CSS
    html += '''
        <table width="1000" align="center">
        <th id="cabecalho" width="300"># Unidade</th>
        <th id="cabecalho" width="200">Lançamento</th>
        <th id="cabecalho" width="60">Atraso Doc</th>
        <th id="cabecalho" width="60">Atraso Lan</th>
        <th id="cabecalho" width="60">Doc</th>
        <th id="cabecalho" width="300">Fornecedor</th>
        <th id="cabecalho" width="100">Data</th>
        '''
    # body_text = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8"></head>'''
    # body_text += '''<pre>    Unidade                    Doc         Fornecedor                       Data        Numero          Lançamento      Atraso doc   Atraso Lan    <br>'''
    sql = '''SELECT cm_unit_id, unidades.un_name,
         comitments_unit.cm_value
        FROM comitments_unit,unidades
        where un_activa=True and cm_act_id=22
        and unidades.un_id= comitments_unit.cm_unit_id
        order by un_name asc'''
    dataset = query_many(sql, (True,))
    xl = dataset
    
    for n in xl:
        sql = 'select us_value1 from unit_settings where us_act_id = 13 and us_unit_id = %s'
        ddns = query_many(sql, (n[0],))[0][0]
        bc = get_info(ddns)
        if bc[0] == -1:
            print n[0], bc[1]
        else:
        #     a = '{:<30}'.format(n[1]) + '{:^6}'.format(str(bc[0])) + '{:<35}'.format(bc[1]) +\
        # '{:<12}'.format(bc[2]) + '{:<18}'.format(bc[3]) + '{:<18}'.format(bc[4]) + '{:>10}'.format(str(bc[5].days + 1)) +\
        # '{:>10}'.format(str(bc[6].days + 1)) + '''<br>'''
        #     body_text += a
            html += '''<tr class="cores">'''
            html += '''<td id="linha_encP" align="left">''' + str(n[1]) + '</td>\n'
            html += '''<td id="linha_encP" align="center">''' + str(bc[4]) + '</td>\n'
            html += '''<td id="linha_encP" align="right">''' + str(bc[6].days + 1) + '</td>\n'
            html += '''<td id="linha_encP" align="right">''' + str(bc[5].days + 1) + '</td>\n'
            html += '''<td id="linha_encP" align="center">''' + str(bc[0]) + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + str(bc[1]) + '</td>\n'
            html += '''<td id="linha_encP" align="center">''' + str(bc[2]) + '</td>\n'
            html += '</tr>\n'
    html += '</table>'
    
    msg_dic = {
        'sub': u'Lançamentos de Facturas em  ' + datetime.datetime.now().strftime("%d %b %Y"),
        'body': html}
    send_mail(['gerencia@espiridiao.pt', 'toze@espiridiao.net', 'ruben@espiridiao.net', 'alexandra@espiridiao.net'], [], msg_dic)
    # send_mail(['gerencia@espiridiao.pt'], [], msg_dic)


def get_info(ddns):
    sql = '''select purchases_.id, suppliers.name, to_char(docdate, 'DD.Mon.YYYY') as last_date,
         supplier_docref, to_char(date_time_stamp,'DD.Mon.YYYY HH24:MI') dt, docdate - now(),
         now()-date_time_stamp
            from purchases_, suppliers
            where suppliers.id=supplier_id and  doctype_id=5
            order by date_time_stamp desc'''
    try:
        conn = psycopg2.connect('host=' + ddns + ' dbname=insoft user=root '
                                                 'password=1n_0rn45+mmiVE591r1_140mmXiii connect_timeout=3')
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, (True,))
        output = cur.fetchone()
        cur.close()
        conn.close()
        return output
    except Exception as e:
        print('-' * 40)
        print(str(e) + '\n -- SQL Error --\n in :\n' + sql)
        print('-' * 40)
        return -1, 'Connetction fail'



if __name__ == "__main__":
    # 24-11-2019
    global CSS
    CSS = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8">
            <style> body { background-color: #ffffff; font-size: 11x; font-family: Verdana; padding: 0; margin: 0;
            height: 100%; } tr.cores { background-color: #FFFFFF; } tr.cores:hover {
            background-color: #F8FBBD; } #linha_encP { border-bottom: solid #CCC 1.0pt; font-family: Verdana;
            font-size: 11px; color: #333333; height: 18px; } #linha2 { border-bottom: solid #0066CC 1.5pt;
            border-top: solid #0066CC 1.5pt; font-family: Verdana; font-size: 15px; color: #000080; height: 15px;
            background-color: #EAF1F7; } .cabecalho { border-top: solid #000 2.0pt; border-bottom: solid #000 1.0pt;
            font-weight: bold; font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 11px;
            background-color: #F8F8F8; } #caixa { border: solid #CCC 1.0pt; text-align: center; font-family: Verdana;
            font-size: 10px; color: #333; font-weight: bold; vertical-align: middle; height: 20px; } </style> '''
    global CSS1
    CSS1 = '''body
            { background-color: #ffffff; font-size: 11x; font-family: Verdana; padding: 0; margin: 0; height: 100%; }
            tr.cores { background-color: #FFFFFF; } tr.cores:hover { background-color: #F8FBBD; } #linha_encP {
                border-bottom: solid #CCC 1.0pt; font-family: Verdana; font-size: 11px; color: #333333; height: 18px; }
            #linha2 { border-bottom: solid #0066CC 1.5pt; border-top: solid #0066CC 1.5pt; font-family: Verdana; font-size: 15px;
            color: #000080; height: 15px; background-color: #EAF1F7; } .cabecalho { border-top: solid #000 2.0pt;
            border-bottom: solid #000 1.0pt; font-weight: bold; font-family: Verdana, Arial, Helvetica, sans-serif;
            font-size: 11px; background-color: #F8F8F8; } #caixa { border: solid #CCC 1.0pt; text-align: center; font-family: Verdana; font-size: 10px;
            color: #333; font-weight: bold; vertical-align: middle; height: 20px; }'''
    software_block_date()
    call_center_to_end()
    call_center_to_end(30,-10)
    software_expire_date()

    
