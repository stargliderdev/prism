#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import uuid

from PyQt5.QtWidgets import QDialog, QApplication, \
    QTableWidget, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QComboBox, QHBoxLayout, QToolButton, QLabel, \
    QTableWidgetItem, QWidget, QCheckBox, QFileDialog, QMessageBox

import sys

import data_sets
import libpg
import msg_sender
import qlib as qc
import parameters as gl

class TestClass(QDialog):
    def __init__(self, data_dict,  parent=None):
        super(TestClass, self).__init__(parent)
        self.resize(1024, 768)
        self.data_dict = data_dict
        if data_dict['type'] == 2:
            self.setWindowTitle('E-mail')
        else:
            self.setWindowTitle('SMS')
    
        self.gridContacts = QTableWidget()
        self.gridContacts.setMaximumWidth(400)
        self.gridContacts.verticalHeader().setDefaultSectionSize(20)
        self.gridContacts.setAlternatingRowColors(True)
        self.gridContacts.setStyleSheet("alternate-background-color: #fff9e6;")
        self.gridContacts.verticalHeader().setVisible(False)
        self.gridContacts.horizontalHeader().setVisible(False)
    
        masterLayout = QHBoxLayout(self)
        masterLayout.addWidget(self.gridContacts)
        sideLayout = QVBoxLayout()
        self.toEdt = QLineEdit()
        sideLayout.addLayout(qc.addVLayout(['para',self.toEdt]))
        if data_dict['type'] == 2:
            self.attachedEdt = QTextEdit()
            self.attBtn = QToolButton()
            self.attBtn.clicked.connect(self.attach_files)
    
        self.cannedCbx = QComboBox()
        # self.cannedCbx.setEditable(True)
        self.cannedCbx.addItems(gl.canned_msg_sms)
        self.cannedCbx.setCurrentIndex(-1)
        self.cannedCbx.editTextChanged.connect(self.canned_msg_change)
        self.cannedCbx.currentIndexChanged.connect(self.canned_msg_change)
        if data_dict['type'] == 2:
            self.cannedCbx.setEditable(True)
            sideLayout.addLayout(qc.addVLayout(['Ficheiros a enviar',self.attachedEdt,self.attBtn]))
    
        sideLayout.addWidget(self.cannedCbx)
        self.textMsgTEdt = QTextEdit()
        self.subjectLbl = QLabel('')
        sideLayout.addWidget(self.subjectLbl)
        if data_dict['type'] == 1:
            self.textMsgTEdt.textChanged.connect(self.count_size)
    
    
        sideLayout.addLayout(qc.addVLayout(['Mensagem', self.textMsgTEdt]))
        # sideLayout.addStretch()
        sendBtn = QPushButton('Envia')
        sendBtn.clicked.connect(self.send_click)
    
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(sendBtn)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_click)
    
        btnLayout.addWidget(cancelBtn)
        sideLayout.addLayout(btnLayout)
        masterLayout.addLayout(sideLayout)
    
        self.refresh_grid()
        
    def refresh_grid(self):
        hl = libpg.query_many('''select contact_types.ctt_name, contacts.ct_value1, contacts.ct_value2
                from unidades
                inner join contacts on ct_unit = un_id
                inner join contact_types on ctt_id = ct_ctt_id
                where un_id = %s  and ctt_way=%s''', (self.data_dict['unit_id'], self.data_dict['type']))
        self.gridContacts.setColumnCount(4)
        # self.gridContacts.setHorizontalHeaderLabels(headers)
        self.gridContacts.setRowCount(len(hl))
        line = 0
        for n in hl:
            self.gridContacts.setCellWidget(line, 0, checkBoxGrid())
            item = QTableWidgetItem()
            item.setText(n[0])
            self.gridContacts.setItem(line,1,item)
            item = QTableWidgetItem()
            item.setText(n[1])
            self.gridContacts.setItem(line,2,item)
            item = QTableWidgetItem()
            item.setText(n[2])
            self.gridContacts.setItem(line,3, item)
            line += 1
        self.gridContacts.setColumnWidth(0, 10)
        self.gridContacts.setColumnWidth(1, 180)
        self.gridContacts.setColumnWidth(2, 110)
        # self.gridContacts.setColumnWidth(3, 0)

    def refresh_label(self):
        if self.data_dict['type'] == 2:
            preview = 'NIF:' + gl.unit_dict['cl_nif'] + ' ' + self.cannedCbx.currentText()
            self.subjectLbl.setText(preview)
        else:
            xl = libpg.query_one('SELECT * FROM msg_canned WHERE LOWER(canned_name) = %s and canned_type = %s ',
                                  (self.cannedCbx.currentText().lower(), self.data_dict['type'] ))

            if xl[6] == 1 :
                self.textMsgTEdt.setText(xl[4])
            else:
                print('vai buscar outra info')
                self.textMsgTEdt.setText(xl[4])
    
    def count_size(self):
        self.subjectLbl.setText(str(len(self.textMsgTEdt.toPlainText())))
    
    def canned_msg_change(self):
        self.refresh_label()
    
    def attach_files(self):
        print('add att')
        file_list = QFileDialog.getOpenFileNames(self, 'Open file','/home/zorze/tmp')
        self.att_files = []
        a = ''
        if file_list == '':
            # vazio
            pass
        else:
            for n in file_list[0]:
                self.att_files.append(str(n))
                c = os.path.basename(str(n))
                a = a + ';' + c
            print(a)
            self.attachedEdt.setText(a.replace(';','\n'))

    def send_click(self):
        print('send')
        send_to = []
        msg_uuid = str(uuid.uuid4())
        if self.data_dict['type'] == 1:
            msg_cnt = 0
            for n in range(0, self.gridContacts.rowCount()):
                if self.gridContacts.cellWidget(n, 0).layout().itemAt(1).widget().isChecked():
                    send_to.append((self.gridContacts.item(n, 3).text(),'toto'))
            for n in send_to:
                # send_to_mobile = {}
                send_to_mobile = msg_sender.send_sms(self.textMsgTEdt.toPlainText(), n[0])
                send_to_mobile['status'] = 0
                send_to_mobile['saldo'] = '1'
                send_to_mobile['return_msg'] = 'dddddd'
        
                if send_to_mobile['status'] != 0:
                    sms_error = 'Estado: ' + str(send_to_mobile['status']) + ' Erro: ' + send_to_mobile['return_msg']
                    void = QMessageBox.critical(self, "Erro", 'Mensagem não enviada\n' + sms_error, QMessageBox.StandardButtons(QMessageBox.Ok))
                    msg_cnt = -1
                    break
                else:
                    msg_cnt += 1
                    log_message({'msg_uuid': msg_uuid, 'type': 1, 'msg_to': str(n[0]), 'msg_to_name': n[1], 'msg_subject': 'SMS', 'msg_body': self.textMsgTEdt.toPlainText(), 'msg_files': ''})
                
            if msg_cnt >0:
                sms_error = 'Saldo: ' + send_to_mobile['saldo']
                void = QMessageBox.information(self, "Info", 'Mensagem enviada' + str(msg_cnt) + '\n' + sms_error,
                                                   QMessageBox.StandardButtons(QMessageBox.Ok))
                
        else:
            send_to = ''
            if self.validate():
                for linha in range(0, self.gridContacts.rowCount()):
                    if self.gridContacts.item(linha, 0) is not None:
                        pass
                    else:
                        if self.gridContacts.cellWidget(linha, 0).layout().itemAt(1).widget().isChecked():
                            send_to += self.gridContacts.item(linha, 3).text()
                print('TO:', send_to)
                print('SUBJECT:', self.subjectLbl.text())
                print('HEADER:', self.canned_data['canned_header'])
                dum = self.textMsgTEdt.toPlainText()
                dum = dum.replace('\n','<br>')
                print('MSG', dum)
                if self.attachedEdt.toPlainText() != '':
                    print('ATTACHEMENTS', self.attachedEdt.toPlainText())
                else:
                    print('NO ATTACHEMENTS')
                print('DETAIL LEVEL', self.canned_data['canned_detail_level'])
                print('FOOTER')
        
    def validate(self):
        flag = True
        self.canned_data = data_sets.canned_msg_to_dict(self.cannedCbx.currentText())
        if self.cannedCbx.currentIndex() == -1:
            QMessageBox.critical(None, "Erro", "É necessario escolher uma mensagem enlatada..")
            flag = False
        else:
            if self.canned_data['canned_files']:
                QMessageBox.critical(None, "Erro", "Esta mensagem necessita de ficheiros.")
                flag = False
        return flag
        
    def cancel_click(self):
        self.close()
    

def log_message(data_dict):
    
    # print( msg_uuid,data_dict['type'], data_dict['msg_to'], data_dict['msg_subject'], data_dict['msg_body'], data_dict['msg_files'], 'test')
    libpg.execute_query('insert into msg_log (msg_uuid, msg_type, msg_to, msg_to_name,  msg_subject, msg_body, msg_files, msg_who) '
                        'values (%s,%s,%s,%s,%s,%s,%s,%s)',
                        (data_dict['msg_uuid'],
                         data_dict['type'],
                         data_dict['msg_to'],
                         data_dict['msg_to_name'],
                         data_dict['msg_subject'],
                         data_dict['msg_body'],
                         data_dict['msg_files'], 'test'))

    
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
    data_sets.get_canned_messages(1)
    app = QApplication(sys.argv)
    form = TestClass({'type': 1, 'unit_id': 0})
    form.show()
    app.exec_()

    
if __name__ == '__main__':
    main()
    # log_message({'type': 2, 'msg_to': '98938890', 'msg_subject': '', 'msg_body': 'teste de mensagem', 'msg_files': ''})

