#!/usr/bin/python
# -*- coding: utf-8 -*-
import time

import psycopg2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QPalette, QFont
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QDesktopWidget, QMessageBox

import add_info
import liblogos
import msg_sms
import parameters as gl
import process_save
import qlib as qc
import smtpmail
import stdio


class DdnsEdit(QDialog):
    def __init__(self, unit_setting, ddns, owner, parent=None):
        super(DdnsEdit, self).__init__(parent)
        self.resize(768, 600)
        self.center()
        self.unit_setting_id = unit_setting
        self.ddns: str = ddns
        self.owner: str = owner
        self.ddns_error: str
        self.setWindowTitle('Edita/Testa DDNS')
        masterLayout = QVBoxLayout(self)
        self.ddnsEdt = QLineEdit()
        self.ddnsEdt.setMinimumWidth(300)
        self.ownerEdt = QLineEdit()
        self.ownerEdt.setMinimumWidth(300)
        self.time_out = QLineEdit()
        self.time_out.setText('3')
        self.time_out.setMaximumWidth(30)
        smsInternalBtn = QPushButton('SMS interna')
        smsInternalBtn.clicked.connect(self.send_sms_internal)
        self.makeProcessBtn = QPushButton('Pedido')
        self.makeProcessBtn.setEnabled(False)
        self.makeProcessBtn.clicked.connect(self.make_process_click)
        
        smsClientBtn = QPushButton('SMS Cliente')
        smsClientBtn.clicked.connect(self.send_sms_client)
        
        masterLayout.addLayout(qc.addHLayout(['DDNS:', self.ddnsEdt, 'Time out (s)', self.time_out, smsInternalBtn, self.makeProcessBtn]))
        masterLayout.addLayout(qc.addHLayout(['Proprietário', self.ownerEdt, smsClientBtn]))
        self.outputPlainText = QTextEdit()
        palette = QPalette()
        brush = QBrush(QColor(0, 255, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Text, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        brush = QBrush(QColor(0, 255, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        brush = QBrush(QColor(165, 164, 164))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush)
        brush = QBrush(QColor(244, 244, 244))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush)
        font = QFont('courier new', 10)
        font.setWeight(80)
        font.setBold(False)
        self.outputPlainText.setPalette(palette)
        self.outputPlainText.setFont(font)
        masterLayout.addWidget(self.outputPlainText)
        okBtn = QPushButton('Valida')
        okBtn.clicked.connect(self.save_click)
        testBtn = QPushButton('Testa')
        testBtn.clicked.connect(self.ddns_test_click)
        
        cancelBtn = QPushButton('Sair')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        
        masterLayout.addLayout(qc.addHLayout([okBtn, testBtn, cancelBtn]))
        # if self.unit_setting_id == -1:
        #     pass
        # else:
        if self.ddns is None:
            pass
        else:
            self.ddnsEdt.setText(self.ddns)
            self.ownerEdt.setText(self.owner)
    
    def cancel_btn_click(self):
        self.close()
    
    def send_sms_internal(self):
        form = msg_sms.MsgSendSMS({'un_id': 0, 'cl_cc': 0, 'ddns': self.ddnsEdt.text()})
        form.exec_()
    
    def send_sms_client(self):
        form = msg_sms.MsgSendSMS(gl.unit_dict)
        form.exec_()
    
    def make_process_click(self):
        x_dict = {'problem': self.ddns_error, 'proc_type': 'DDNS'}
        form = add_info.AddInfo()
        form.exec_()
        if form.ret[0]:
            x_dict.update(form.ret[1])
            process_id: int = process_save.intervention(x_dict)
            smtpmail.send_process_mail(process_id)
            QMessageBox.critical(None, "Info", "Processo criado " + str(process_id))
            self.close()
        
    def ddns_test_click(self):
        self.ddns = self.ddnsEdt.text()
        self.outputPlainText.setText('Testando DDNS de: ' + self.ddns)
        self.outputPlainText.repaint()
        gl.c = "host=" + self.ddns + ''' dbname=insoft port=5432 user=root password='1n_0rn45+mmiVE591r1_140mmXiii' connect_timeout=''' + self.time_out.text()
        time.sleep(0.23)
        t0 = time.time()
        a = psql_listen()
        if a[0]:
            html = "{:>14}".format('DDNS: ') + self.ddns + '\n'
            html += '-' * 80 + '\n'
            html += self.info_restware_short()
            html += '\n'
            html += self.info_psql()
            t1 = time.time()
            html += '\n Respondeu em: ' + str((t1 - t0))[0:4] + ' segundos.'
        else:
            t1 = time.time()
            self.makeProcessBtn.setEnabled(True)
            html = ''' <!DOCTYPE
                    html > < html
                    lang = "pt_pt"> <head> <meta
                    charset = "utf-8" >
                    </head> <br><font size="5" face="verdana" color="red"><strong> ''' + a[1].replace('\n', '<br>') \
                   + '''<strong> <br><font size="3" face="verdana" color="orange">''' + 'Não respondeu em : ' + str(
                (t1 - t0))[0:4] + ''' segundos. </font></html > '''
            self.ddns_error = a[1]
        self.outputPlainText.append(html)
    
    def save_click(self):
        if self.unit_setting_id == -1:
            liblogos.insert_unit_setting(gl.unit_dict['un_id'], 13, self.ddnsEdt.text(), self.ownerEdt.text())
        else:
            liblogos.update_unit_settings(self.unit_setting_id, self.ddnsEdt.text(), self.ownerEdt.text())
        self.close()
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def info_restware_short(self):
        hl = ''
        sql = '''SELECT saftname,dbversion, saftnif, validuntil,commercial_name from params;'''
        d = query_many(sql)[0]
        hl += "{:>14}".format('D. Social:') + d[0] + '\n'
        hl += "{:>14}".format('D. Comercial:') + d[4] + '\n'
        hl += "{:>14}".format('dbversion:') + d[1] + '\n'
        hl += "{:>14}".format('NIF:') + d[2] + '\n'
        hl += "{:>14}".format('Validade:') + str(d[3]) + '\n'
        return hl
    
    def info_psql(self):
        sql = 'SELECT version();'
        a = query_many(sql, (True,))
        a = str(a[0])
        a = a.replace('(', '')
        a = a.split(',')
        tx = 'Server Version:' + str(a[0]) + ' ' + str(a[2]) + '\n'
        sql = """SELECT current_timestamp,current_timestamp - pg_postmaster_start_time(), pg_postmaster_start_time(),pg_database_size(%s);"""
        a = query_one(sql, ('insoft',))
        tx += '   Server date: ' + a[0].strftime("%Y-%m-%d %H:%M") + '\n'
        tx += ' Server uptime: ' + str(a[1]) + '\n'
        tx += '  Server start: ' + a[2].strftime("%Y-%m-%d %H:%M") + '\n'
        b = str(a[3]) + '/' + stdio.pretty_size((a[3] / 100 * 10))
        b = stdio.pretty_size((a[3] / 100 * 10))
        tx += '     File size: ' + b + '\n'
        return tx


def query_one(sql, data=(True,)):
    try:
        conn = psycopg2.connect(gl.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        xl = cur.fetchone()
        cur.close()
        conn.close()
        return xl
    except Exception as e:
        return str(e) + '\n -- SQL Error --\n in :' + '\n' + sql


def query_many(sql, data=(True,)):
    try:
        conn = psycopg2.connect(gl.c)
        cur = conn.cursor()
        # conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        xl = cur.fetchall()
        cur.close()
        conn.close()
        return xl
    except Exception as e:
        return str(e) + '---------\b\n' + sql


def psql_listen():
    try:
        conn = psycopg2.connect(gl.c)
        conn.close()
        return True, 'OK'
    except psycopg2.OperationalError as ex:
        return False, "Connection failed: {0}".format(ex)


if __name__ == '__main__':
    pass
