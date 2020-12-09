#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import sys
import uuid

from PyQt5.QtWidgets import QDialog, QApplication, \
    QTableWidget, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QComboBox, QHBoxLayout, \
    QTableWidgetItem, QWidget, QCheckBox, QMessageBox,QStyleFactory,QToolButton
from PyQt5.QtGui import QIcon, QFont


import data_sets
import libpg
import msg_sender
import parameters as gl
import qlib as qc
import smtpmail


class MsgEmailSend(QDialog):
    def __init__(self, data_dict, parent=None):
        super(MsgEmailSend, self).__init__(parent)
        self.resize(1024, 768)
        self.data_dict = data_dict
        self.setWindowTitle('SMS')
        self.data_dict['type'] = 2
        self.gridContacts = QTableWidget()
        # self.gridContacts.setMaximumWidth(400)
        self.gridContacts.verticalHeader().setDefaultSectionSize(20)
        self.gridContacts.setAlternatingRowColors(True)
        self.gridContacts.setStyleSheet("alternate-background-color: #fff9e6;")
        self.gridContacts.verticalHeader().setVisible(False)
        self.gridContacts.horizontalHeader().setVisible(False)
        self.gridContacts.setMaximumHeight(200)
        
        masterLayout = QVBoxLayout(self)
        masterLayout.addWidget(self.gridContacts)
        self.toEdt = QLineEdit()
        
        self.cannedCbx = QComboBox()
        self.cannedCbx.addItems(gl.canned_msg_mail)
        self.cannedCbx.setCurrentIndex(-1)
        self.cannedCbx.editTextChanged.connect(self.canned_msg_change)
        self.cannedCbx.currentIndexChanged.connect(self.canned_msg_change)
        
        masterLayout.addWidget(self.cannedCbx)
        self.textMsgTEdt = QTextEdit()
        self.subjectEdt = QLineEdit()
        masterLayout.addWidget(self.subjectEdt)
        # insertPicturBtn = QToolButton()
        # insertPicturBtn.setToolTip('Cola o relatório da ultima avaria/sintoma')
        # insertPicturBtn.setIcon(QIcon('.//img//paste.png'))
        # insertPicturBtn.clicked.connect(self.insert_picture_click)
        #
        attacheFileBtn = QToolButton()
        attacheFileBtn.setToolTip('Cola o relatório da ultima avaria/sintoma')
        attacheFileBtn.setIcon(QIcon('.//img//paste.png'))
        # insertPicturBtn.clicked.connect(self.last_issue_paste)
        
        masterLayout.addLayout(qc.addHLayout(['Mensagem',  attacheFileBtn,True]))
        masterLayout.addWidget(self.textMsgTEdt,)
        self.sendBtn = QPushButton('Envia')
        self.sendBtn.clicked.connect(self.send_click)
        
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.sendBtn)
        cancelBtn = QPushButton('Sair')
        cancelBtn.clicked.connect(self.cancel_click)
        btnLayout.addWidget(cancelBtn)
        masterLayout.addLayout(btnLayout)
        self.refresh_grid()
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        
    def refresh_grid(self):
        """ todos os contactos menos os horarios e folga incluindo todos os da unidade 0"""
        hl = libpg.query_many('''select contact_types.ctt_name, contacts.ct_value1, contacts.ct_value2
                from unidades
                inner join contacts on ct_unit = un_id
                inner join contact_types on ctt_id = ct_ctt_id
                where (un_id = %s or un_id=0) and ctt_way= %s order by ctt_group, ctt_order''', (self.data_dict['unit_id'],2))
        self.gridContacts.setColumnCount(4)
        # self.gridContacts.setHorizontalHeaderLabels(headers)
        self.gridContacts.setRowCount(len(hl))
        line = 0
        for n in hl:
            self.gridContacts.setCellWidget(line, 0, checkBoxGrid())
            item = QTableWidgetItem()
            item.setText(n[2])
            self.gridContacts.setItem(line, 1, item)
            item = QTableWidgetItem()
            item.setText(n[1])
            self.gridContacts.setItem(line, 2, item)
            item = QTableWidgetItem()
            item.setText(n[0])
            self.gridContacts.setItem(line, 3, item)
            line += 1
        self.gridContacts.setColumnWidth(0, 10)
        self.gridContacts.setColumnWidth(1, 280)
        self.gridContacts.setColumnWidth(2, 180)
        self.gridContacts.setColumnWidth(3, 280)
    
    def refresh_label(self):
        xl = libpg.query_one('SELECT * FROM msg_canned WHERE LOWER(canned_name) = %s and canned_type = %s ',
                             (self.cannedCbx.currentText().lower(), 2))
        self.textMsgTEdt.clear()
        if xl[6] == 1:
            self.textMsgTEdt.setText(xl[4])
        else:
            # vai buscar outra info')
            if xl[0] in (5, 7):
                """ conta corrente"""
                dum = xl[4]
                dum = dum.replace('$', "{:.2f}".format(self.data_dict['cl_cc']))
                self.textMsgTEdt.setHtml(dum)
            elif xl[0] == 9:
                """envia DDNS ok internamente"""
                dum = xl[4]
                ddns = data_sets.get_one_setting(gl.unit_dict['un_id'], 13)[0]
                dum = dum.replace('$', ddns)
                self.textMsgTEdt.setText(dum)
            elif xl[0] == 10:
                """envia BO a funcionar para o cliente"""
                dum = xl[4]
                dum = dum.replace('$', self.data_dict['un_name'])
                self.textMsgTEdt.setText(dum)
    
    def insert_picture_click(self):
        pass
    
    def count_size(self):
        self.subjectLbl.setText(str(len(self.textMsgTEdt.toPlainText())))
    
    def canned_msg_change(self):
        self.refresh_label()
    
    def send_click(self):
        send_to = []
        msg_uuid = str(uuid.uuid4())
        msg_cnt = 0
        for n in range(0, self.gridContacts.rowCount()):
            if self.gridContacts.cellWidget(n, 0).layout().itemAt(1).widget().isChecked():
                send_to.append((self.gridContacts.item(n, 1).text(), self.gridContacts.item(n, 2).text()))
        if len(send_to) == 0:
            void = QMessageBox.critical(self, "Erro", 'Sem Destinatarios ', QMessageBox.StandardButtons(QMessageBox.Ok))
        else:
            for n in send_to:
                send_to_mobile = msg_sender.send_sms(self.textMsgTEdt.toPlainText(), n[0])
                if send_to_mobile['status'] != 0:
                    sms_error = 'Estado: ' + str(send_to_mobile['status']) + ' Erro: ' + send_to_mobile['return_msg']
                    void = QMessageBox.critical(self, "Erro", 'Mensagem não enviada\n' + sms_error,
                                                QMessageBox.StandardButtons(QMessageBox.Ok))
                    msg_cnt = -1
                    break
                else:
                    msg_cnt += 1
                    self.log_message({'msg_uuid': msg_uuid, 'type': 2, 'msg_to': str(n[0]), 'msg_to_name': n[1], 'msg_subject': 'SMS','msg_body': self.textMsgTEdt.toPlainText(), 'msg_files': ''})
                    sub = '[SMS] ' + gl.unit_dict['un_name'] + ' :' + self.textMsgTEdt.toPlainText()
                    body = 'Unidade: ' + gl.unit_dict['un_name'] + '<br> Para: ' + n[1] + '[' + str(n[0]) + ']' + '<br>Conteudo: <hr><pre>' + self.textMsgTEdt.toPlainText().replace('\n', '<br>')
                    body += '<hr></pre>'
                    body += 'quem:' + gl.user_dict['user_name'] + '<br>' + datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
                    smtpmail.send_sms_mail({'sub': sub, 'body': body})
    
            # if msg_cnt > 0:
            #     sms_error = 'Saldo: ' + send_to_mobile['saldo']
            #     void = QMessageBox.information(self, "Info", 'Mensagen(s) enviada(s) ' + str(msg_cnt) + '\n' + sms_error,
            #                                    QMessageBox.StandardButtons(QMessageBox.Ok))
            #     self.sendBtn.setText('Enviada! Re-enviar')
            # else:
            #     smtpmail.send_sms_mail({'sub': 'Erro ao enviar SMS', 'body': 'Erro ao enviar SMS <br> ' + sms_error})
        
    def validate(self):
        flag = True
        self.canned_data = data_sets.canned_msg_to_dict(self.cannedCbx.currentText())
        if self.cannedCbx.currentIndex() == -1:
            QMessageBox.critical(None, "Erro", "É necessario escolher uma mensagem enlatada..")
            flag = False
        return flag
    
    def cancel_click(self):
        self.close()
    
    def log_message(self, msg_dict):
        # print( msg_uuid,data_dict['type'], data_dict['msg_to'], data_dict['msg_subject'], data_dict['msg_body'], data_dict['msg_files'], 'test')
        libpg.execute_query(
            'insert into msg_log (msg_unit_id, msg_uuid, msg_type, msg_to, msg_to_name,  msg_subject, msg_body, msg_files, msg_who) '
            'values (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (self.data_dict['un_id'], msg_dict['msg_uuid'],
             msg_dict['type'],
             msg_dict['msg_to'],
             msg_dict['msg_to_name'],
             msg_dict['msg_subject'],
             msg_dict['msg_body'],
             msg_dict['msg_files'], gl.user_dict['user_name']))


def checkBoxGrid(label=''):
    w = QWidget()
    l = QHBoxLayout(w)
    l.setContentsMargins(0, 0, 0, 0)
    l.addStretch()
    c = QCheckBox(label)
    l.addWidget(c)
    l.addStretch()
    return w


def main():
    gl.unit_dict = data_sets.unit_to_dic(0)
    data_sets.get_canned_messages_mail()
    app = QApplication(sys.argv)
    form = MsgEmailSend({'type': 1, 'unit_id': 225})
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
    # log_message({'type': 2, 'msg_to': '98938890', 'msg_subject': '', 'msg_body': 'teste de mensagem', 'msg_files': ''})
