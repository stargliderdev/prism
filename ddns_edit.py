#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import datetime

import psycopg2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QPalette, QFont, QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QDesktopWidget, QMessageBox, \
    QToolButton, QApplication

import add_info
import liblogos
import libpg
import msg_sms
import parameters as gl
import process_save
import qlib as qc
import smtpmail
import stdio


class DdnsEdit(QDialog):
    def __init__(self, unit_setting, data, parent=None):
        super(DdnsEdit, self).__init__(parent)
        self.resize(768, 600)
        self.center()
        self.unit_setting_id = unit_setting
        self.comm_status: str = ''
        # if not data is None:
        #     self.ddns: str = data[0]
        #     self.owner: str = data[1]
        self.ddns_error: str
        self.data = data
        self.clipboard = QApplication.clipboard()
        self.setWindowTitle('Edita/Testa DDNS')
        masterLayout = QVBoxLayout(self)
        self.ddnsEdt = QLineEdit()
        self.ddnsEdt.setMinimumWidth(300)
        self.ownerEdt = QLineEdit()
        self.ownerEdt.setMinimumWidth(300)
        self.time_out = QLineEdit()
        self.time_out.setText('3')
        self.time_out.setMaximumWidth(30)
        self.copyAddTbtn = QToolButton()
        self.copyAddTbtn.clicked.connect(self.copy_to_clipboard)
        self.copyAddTbtn.setIcon(QIcon('.//img//copy.png'))
        smsInternalBtn = QPushButton('SMS interna')
        smsInternalBtn.clicked.connect(self.send_sms_internal)
        self.makeProcessBtn = QPushButton('Cria Pedido')
        self.makeProcessBtn.setEnabled(False)
        self.makeProcessBtn.clicked.connect(self.make_process_click)
        self.closeProcessBtn = QPushButton('Fecha Pedido')
        self.closeProcessBtn.setEnabled(False)
        self.closeProcessBtn.clicked.connect(self.close_process_click)
        smsClientBtn = QPushButton('SMS Cliente')
        smsClientBtn.clicked.connect(self.send_sms_client)
        
        masterLayout.addLayout(qc.addHLayout(
            ['DDNS:', self.ddnsEdt, self.copyAddTbtn, 'Time out (s)', self.time_out, self.makeProcessBtn, self.closeProcessBtn]))
        masterLayout.addLayout(qc.addHLayout(['Proprietário', self.ownerEdt, smsInternalBtn, smsClientBtn]))
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
        okBtn = QPushButton('Grava')
        okBtn.clicked.connect(self.save_click)
        testBtn = QPushButton('Testa')
        testBtn.clicked.connect(self.ddns_test_click)
        
        cancelBtn = QPushButton('Sair')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        
        masterLayout.addLayout(qc.addHLayout([okBtn, testBtn, cancelBtn]))
        if data is None:
            pass
        else:
            self.ddnsEdt.setText(data[0])
            self.ownerEdt.setText(data[1])
        self.has_pend_p = libpg.query_one(
            '''select proc_id, proc_date, proc_reported, proc_quem, proc_tecnico from assistencias where proc_unit_id=%s and proc_type=%s and proc_pendente=True''',
            (gl.unit_dict['un_id'], 'DDNS'))
        gl.date_time_stack = datetime.datetime.now()

    def copy_to_clipboard(self):
        self.clipboard.setText(self.ddnsEdt.text())
    
    def cancel_btn_click(self):
        self.close()
    
    def send_sms_internal(self):
        form = msg_sms.MsgSendSMS({'un_id': 0, 'cl_cc': 0, 'ddns': self.ddnsEdt.text()})
        form.exec_()
    
    def send_sms_client(self):
        form = msg_sms.MsgSendSMS(gl.unit_dict)
        form.exec_()
    
    def make_process_click(self):
        gl.proc_dict.update({'proc_action_report': self.ddns_error,
                  'proc_type': 'DDNS',
                  'proc_date': datetime.datetime.now(),
                  'proc_meio': 'Escritório',
                  'proc_reported': self.comm_status,
                  'proc_status': 'Aguarda n/ Intervenção',
                  'proc_montante': 0,
                  'proc_jusante': -1,
                  'proc_pendente': True,
                  'proc_facturar': False,
                  'proc_type': 'DDNS',
                               })

        form = add_info.AddInfo(gl.proc_dict)
        form.exec_()
        if form.ret[0]:
            gl.proc_dict.update(form.ret[1])
            
            process_id: int = process_save.save_process(gl.proc_dict)
            if process_id[0]:
                smtpmail.send_process_mail(process_id[1])
                # QMessageBox.information(None, "Info", "Processo criado " + str(process_id[1]))
                self.close()
            else:
                QMessageBox.critical(None, "Erro", "Não foi possivel criar um processo")
    
    def close_process_click(self):
        gl.proc_dict.update({'proc_action_report': self.ddns_error,
                             'proc_type': 'DDNS',
                             'proc_date': datetime.datetime.now(),
                             'proc_meio': 'Escritório',
                             'proc_reported': self.comm_status,
                             'proc_status': 'Resolvido',
                             'proc_montante': self.has_pend_p[0],
                             'proc_quem': self.has_pend_p[3],
                             'proc_jusante': 0,
                             'proc_pendente': False,
                             'proc_facturar': False,
                             'proc_type': 'DDNS',
                             'proc_tecnico': self.has_pend_p[4]
                             })
        
        form = add_info.AddInfo(gl.proc_dict)
        form.exec_()
        if form.ret[0]:
            gl.proc_dict.update(form.ret[1])
            # gl.proc_dict['proce_report_internal'] = gl.proc_dict['proc_reported'] + '\n' + gl.proc_dict['proc_action_report']
            process_id: int = process_save.save_process(gl.proc_dict)
            if process_id[0]:
                smtpmail.send_process_mail(process_id[1])
                # QMessageBox.information(None, "Info", "Processo criado " + str(process_id[1]))
                self.close()
            else:
                QMessageBox.critical(None, "Erro", "Não foi possivel criar um processo")
    
    def ddns_test_click(self):
        self.ddns = self.ddnsEdt.text()
        self.outputPlainText.setText('Testando DDNS de: ' + self.ddns)
        self.outputPlainText.repaint()
        gl.c = "host=" + self.ddns + ''' dbname=insoft port=5432 user=root password='1n_0rn45+mmiVE591r1_140mmXiii' connect_timeout=''' + self.time_out.text()
        time.sleep(0.23)
        t0 = time.time()
        a = psql_listen()
        """ pode ser aberto mesmo estando a funcionar."""
        self.makeProcessBtn.setEnabled(True)
        """ pode ser fechado o mesmo dando erro"""
        if self.has_pend_p is None:
            # self.closeProcessBtn.setEnabled(True)
            pass
        else:
            self.makeProcessBtn.setEnabled(False)
            self.closeProcessBtn.setEnabled(True)
        if a[0]:
            html = "{:>14}".format('DDNS:') + self.ddns + '\n'
            # html += '-' * 80 + '\n'
            html += self.info_restware_short()
            html += '\n'
            html += self.info_psql()
            t1 = time.time()
            html += '\n Respondeu em: ' + str((t1 - t0))[0:4] + ' segundos.'
            self.ddns_error = html
            self.comm_status = 'Verificado e a funcionar'
        else:
            t1 = time.time()
            # if self.has_pend_p is None:

            html = ''' <!DOCTYPE
                    html > < html
                    lang = "pt_pt"> <head> <meta
                    charset = "utf-8" >
                    </head> <br><font size="5" face="verdana" color="red"><strong> ''' + a[1].replace('\n', '<br>') \
                   + '''<strong> <br><font size="3" face="verdana" color="orange">''' + 'Não respondeu em : ' + str(
                (t1 - t0))[0:4] + ''' segundos. </font></html > '''
            self.comm_status = 'Erro nas comunicações'
            self.ddns_error = a[1]
        self.outputPlainText.append(html)
    
    def save_click(self):
        if self.data is None:
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
        sql = '''SELECT saftname,dbversion, saftnif, validuntil,commercial_name, TO_CHAR(age(validuntil,'now'), 'DD ') || 'Dias'  FROM params;'''
        d = query_many(sql)[0]
        hl += "{:>14}".format('D. Social:') + d[0] + '\n'
        hl += "{:>14}".format('D. Comercial:') + d[4] + '\n'
        hl += "{:>14}".format('dbversion:') + d[1] + '\n'
        hl += "{:>14}".format('NIF:') + d[2] + '\n'
        if d[3].year == 2050:
            hl += "{:>14}".format('Validade:' + 'Desbloqueado') + '\n'
        else:
            hl += "{:>14}".format('Validade:') + d[3].strftime("%Y-%m-%d") + ' [' + d[5] + ']' + '\n'
        return hl
    
    def info_psql(self):
        sql = 'SELECT version();'
        a = query_many(sql, (True,))
        a = str(a[0]).replace('\'','')
        a = a.replace('(', '')
        a = a.split(',')
        tx = 'Server Version:' + str(a[0]) + ' ' + str(a[2]) + '\n'
        sql = """SELECT current_timestamp,current_timestamp - pg_postmaster_start_time(), pg_postmaster_start_time(),pg_database_size(%s);"""
        a = query_one(sql, ('insoft',))
        tx += '   Server date: ' + a[0].strftime("%Y-%m-%d %H:%M") + '\n'
        tx += ' Server uptime: ' + str(a[1]) + '\n'
        tx += '  Server start: ' + a[2].strftime("%Y-%m-%d %H:%M") + '\n'
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
