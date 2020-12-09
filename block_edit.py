#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import time
import datetime
import random
import psycopg2
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QDesktopWidget, QMessageBox, \
    QApplication, QCalendarWidget, QComboBox
import data_sets
import libpg
import parameters as gl
import process_save
import qlib as qc
import smtpmail


class BlockSoftware(QDialog):
    def __init__(self, parent=None):
        super(BlockSoftware, self).__init__(parent)
        # self.resize(768, 600)
        self.order_id = 2
        self.center()
        self.setWindowTitle('Bloqueia Software')
        masterLayout = QVBoxLayout(self)
        self.balanceEdt = QLineEdit()
        self.balanceEdt.setReadOnly(True)
        self.daysToLock = QComboBox()
        self.daysToLock.addItems(['Desbloqueia','1 Dia','4 dias','8 dias','15 dias', '30 dias'])
        self.reasonCBox = QComboBox()
        self.reasonCBox.addItems(gl.motif_block)
        masterLayout.addLayout(qc.addHLayout(['Saldo:', self.balanceEdt], lw=60))
        masterLayout.addLayout(qc.addHLayout(['Dias',self.daysToLock], lw=60))
        masterLayout.addLayout(qc.addHLayout(['Motivo', self.reasonCBox], lw=60))
        self.calendar_QCalendarWidget = QCalendarWidget()
        self.calendar_QCalendarWidget.setMinimumDate(datetime.datetime.now()+datetime.timedelta(days=1))
        self.calendar_QCalendarWidget.setVerticalHeaderFormat(0)
        self.msgText = QTextEdit()
        masterLayout.addWidget(self.calendar_QCalendarWidget)
        masterLayout.addWidget(self.msgText)
        makeRequest = QPushButton('Pedido')
        makeRequest.clicked.connect(self.local_request)
        self.remoteLockBtn = QPushButton('Directo')
        self.remoteLockBtn.setEnabled(True)
        self.remoteLockBtn.clicked.connect(self.remote_request)
        
        cancelBtn = QPushButton('Sair')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        
        masterLayout.addLayout(qc.addHLayout([makeRequest, self.remoteLockBtn, cancelBtn]))
        self.daysToLock.currentIndexChanged.connect(self.days_change)
        self.daysToLock.setCurrentIndex(3)
        self.balanceEdt.setText('{0:.2f}'.format(gl.unit_dict['cl_cc']))
        if gl.unit_dict['cl_cc'] == 0:
            self.reasonCBox.setCurrentIndex(0)
            self.daysToLock.setCurrentIndex(0)
        self.ddns = data_sets.get_one_setting(gl.unit_dict['un_id'], 13)[0]
        if self.ddns == '':
            self.remoteLockBtn.setEnabled(False)
        
    
    def cancel_btn_click(self):
        self.close()
    
    
    def days_change(self):
        if self.daysToLock.currentIndex() ==0:
            self.calendar_QCalendarWidget.setEnabled(False)
        else:
            a = self.daysToLock.currentText().split()
            """escolhe um dia de 3 a 5"""
            rd = random.randint(1,3)
            good_day = last_monday(datetime.datetime.now() + datetime.timedelta(days=int(a[0]))) + datetime.timedelta(days=rd)
            self.calendar_QCalendarWidget.setSelectedDate(good_day)
    
    def make_block_request(self):
        gl.proc_dict['proc_action_report'] = '    Duração:' + self.daysToLock.currentText() + '\n' +\
                                               '   Bloqueia:' + self.calendar_QCalendarWidget.selectedDate().toPyDate().strftime('%d-%m-%Y') + '\n' +\
                                               'C.C. á data:' + '{0:.2f}'.format(gl.unit_dict['cl_cc']) + '\n' + \
                                               '     Motivo:' + self.reasonCBox.currentText() + '\n' + \
                                                self.msgText.toPlainText()
        gl.proc_dict.update({'proc_type': 'BLCK',
                             'proc_date': datetime.datetime.now(),
                             'proc_meio': 'Escritório',
                             'proc_reported': '',
                             'proc_status': 'Resolvido',
                             'proc_montante': 0,
                             'proc_quem': 'Todos',
                             'proc_jusante': 0,
                             'proc_pendente': False,
                             'proc_facturar': False,
                             'proc_tecnico': gl.user_dict['user_name'],
                             'proc_source': 'Escritório',
                             'proc_cause_report': 'Bloqueado',
                             'proc_action_report': 'Desbloqueado'
                             })
        process_id: int = process_save.save_process(gl.proc_dict)
        
        if process_id[0]:
            smtpmail.SEND_BLOCK_MAIL(process_id[1], self.order_id,self.calendar_QCalendarWidget.selectedDate().toPyDate().strftime('%d-%m-%Y'))
            libpg.execute_query('update comitments_unit set cm_value=%s where cm_unit_id=%s and cm_act_id=13 ',
                                (self.calendar_QCalendarWidget.selectedDate().toPyDate().strftime('%Y-%m-%d'), gl.unit_dict['un_id']))
            self.close()
        else:
            QMessageBox.critical(None, "Erro", "Não foi possivel criar um processo")
  
  
    def local_request(self):
        if self.daysToLock.currentIndex() == 0:
            self.order_id = 4
            self.calendar_QCalendarWidget.setSelectedDate(datetime.date(2050, 1, 1))
        else:
            self.order_id = 3
        self.make_block_request()
    
    def remote_request(self):
        self.ddns = data_sets.get_one_setting(gl.unit_dict['un_id'], 13)[0]
        gl.c = "host=" + self.ddns + ''' dbname=insoft port=5432 user=root password='1n_0rn45+mmiVE591r1_140mmXiii' connect_timeout=3'''
        time.sleep(0.23)
        a = psql_listen()
        if a[0]:
            """ Respondeu"""
            """carregar a nova data """
            if self.daysToLock.currentIndex() == 0:
                insoft_execute_query("UPDATE params SET validuntil = %s", (datetime.date(2050,1,1),))
                self.order_id = 2
            else:
                insoft_execute_query("UPDATE params SET validuntil = %s", (self.calendar_QCalendarWidget.selectedDate().toPyDate(),))
                self.order_id = 1
            self.make_block_request()
        else:
            """deu erro o DDNS está errado não funciona"""
            # self.order_id = 1
            QMessageBox.critical(None, "Erro", "Não foi possivel ligar ao servidor \n" + self.ddns)

    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    

def psql_listen():
    try:
        conn = psycopg2.connect(gl.c)
        conn.close()
        return True, 'OK'
    except psycopg2.OperationalError as ex:
        return False, "Connection failed: {0}".format(ex)

def insoft_execute_query(sql, data):
    try:
        conn = psycopg2.connect(gl.c)
        cur = conn.cursor()
        # conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        return False

def last_monday(date):
    today = date
    last_monday = today + datetime.timedelta(days=-date.weekday() + 0, weeks=0)
    return last_monday

def main():
    app = QApplication(sys.argv)
    form = BlockSoftware()
    form.show()
    app.exec_()
    
if __name__ == '__main__':
    pass
