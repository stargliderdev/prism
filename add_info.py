#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import datetime

from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout, QLineEdit, QPlainTextEdit, QComboBox, \
    QPushButton, QDateTimeEdit, QLabel, QMessageBox, QToolButton
from PyQt5.QtGui import QIcon

import asterisk_interface
import data_sets
import qlib as qc
import parameters as gl


class AddInfo(QDialog):
    def __init__(self, data_dict, parent=None):
        super(AddInfo, self).__init__(parent)
        masterLayout = QVBoxLayout(self)
        self.resize(600, 400)
        self.setWindowTitle('Adiciona informação ao Pedido')
        self.ret = (False,)
        self.process_dict = {}
        gl.asterisk_stack_call = {}
        self.ddns_text = data_dict['proc_action_report']
        self.proc_whoEdt = QLineEdit()
        labelIssue = QLabel('Avaria/Sintoma/Problema')
        labelIssue.setStyleSheet("font-weight: bold; color: #FF0000;")
        self.proc_reported = QPlainTextEdit()
        labelCause = QLabel('Causa/Origem do problema')
        labelCause.setStyleSheet("font-weight: bold;color: #0066ff;")
        self.proc_cause_report = QPlainTextEdit()
        labelAction = QLabel('Acção')
        labelAction.setStyleSheet("font-weight: bold;color: #33cc33;")
        self.proc_action_report = QPlainTextEdit()
        self.techCbx = QComboBox()
        self.sourceBox = QComboBox()
        self.sourceBox.addItems(gl.proc_sources)
        self.sourceBox.setCurrentIndex(0)
        closeBtn = QPushButton('Fecha')
        closeBtn.clicked.connect(self.close_click)
        pendingBtn = QPushButton('Pendente')
        pendingBtn.clicked.connect(self.pending_click)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_click)
        asteriskLogBtn = QToolButton()
        asteriskLogBtn.setToolTip('Relatório do Asterisk')
        asteriskLogBtn.setIcon(QIcon('.//img//asterisk.png'))
        asteriskLogBtn.clicked.connect(self.asterisk_log_click)
        masterLayout.addLayout(qc.addHLayout(['Técnico', self.techCbx, 'Origem', self.sourceBox]))
        masterLayout.addLayout(qc.addHLayout(['Quem', self.proc_whoEdt, asteriskLogBtn]))
        self.proc_duracao = QDateTimeEdit()
        self.proc_duracao.setMaximumWidth(80)
        self.proc_duracao.setDisplayFormat("hh:mm")
        duration = (datetime.datetime.now() - gl.date_time_stack) + datetime.timedelta(seconds=220)
        a = str(duration).split(':')
        dd = datetime.datetime(1900, 1, 1, int(a[0]), int(a[1]), int(a[2][:2]))
        self.proc_duracao.setDateTime(dd)
        masterLayout.addLayout(qc.addHLayout(['Duração', self.proc_duracao, True]))
        masterLayout.addWidget(labelIssue)
        masterLayout.addWidget(self.proc_reported)
        masterLayout.addWidget(labelCause)
        masterLayout.addWidget(self.proc_cause_report)
        masterLayout.addWidget(labelAction)
        masterLayout.addWidget(self.proc_action_report)
        masterLayout.addLayout(qc.addHLayout([pendingBtn, closeBtn, cancelBtn]))
        
        self.techCbx.addItems(gl.ds_tecnicos)
        
        self.proc_whoEdt.setText(data_dict['proc_quem'])
        if data_dict['proc_quem'] == '':
            self.techCbx.setCurrentText(gl.user_dict['user_name'].title())
        else:
            self.techCbx.setCurrentText(data_dict['proc_tecnico'])
        self.proc_reported.setPlainText(data_dict['proc_reported'])
    
    def close_click(self):
        if self.proc_action_report.toPlainText() == '':
            void = QMessageBox.critical(self, "Erro", 'Falta a Acção: o que foi feito',
                                        QMessageBox.StandardButtons(QMessageBox.Ok))
        else:
            self.process_dict.update({'proc_tecnico': self.techCbx.currentText(),
                                      'proc_quem': self.proc_whoEdt.text(),
                                      'proc_reported': self.proc_reported.toPlainText() + '\n' + self.ddns_text,
                                      'proc_cause_report': self.proc_cause_report.toPlainText(),
                                      'proc_action_report': self.proc_action_report.toPlainText(),
                                      'proc_duracao': str(self.proc_duracao.dateTime().toPyDateTime().hour) + ':' + str(self.proc_duracao.dateTime().toPyDateTime().minute),
                                      'proc_pendente': False,
                                      'proc_status': 'A funcionar',
                                      'proc_source': self.sourceBox.currentText()
                                      })
            self.ret = (True, self.process_dict)
            self.close()
    
    def pending_click(self):
        self.process_dict.update({'proc_tecnico': self.techCbx.currentText(),
                                  'proc_quem': self.proc_whoEdt.text(),
                                  'proc_reported': self.proc_reported.toPlainText() + '\n' + self.ddns_text,
                                  'proc_cause_report': self.proc_cause_report.toPlainText(),
                                  'proc_action_report': self.proc_action_report.toPlainText(),
                                  'proc_duracao': str(self.proc_duracao.dateTime().toPyDateTime().hour) + ':' + str(self.proc_duracao.dateTime().toPyDateTime().minute),
                                  'proc_pendente': True,
                                  'proc_status': 'Pendente de Intervenção',
                                  'proc_source': self.sourceBox.currentText()
                                  })
        self.ret = (True, self.process_dict)
        self.close()
    
    def cancel_click(self):
        self.ret = (False, {})
        self.close()
    
    def asterisk_log_click(self):
        form = asterisk_interface.AsteriskInterface()
        form.exec_()
        gl.asterisk_stack_call = form.toto
        try:
            if gl.asterisk_stack_call['call_number'] == '':
                pass
            else:
                self.proc_whoEdt.setText(
                    gl.asterisk_stack_call['call_who'])  # + ' ' + gl.asterisk_stack_call['call_number'])
                self.process_dict['proc_quem'] = gl.asterisk_stack_call['call_who']
                self.process_dict['proc_asterisk'] = gl.asterisk_stack_call['call_cdr']
                self.process_dict['proc_contacto'] = gl.asterisk_stack_call['call_number']
        except KeyError:
            pass

def main():
    app = QApplication(sys.argv)
    form = AddInfo()
    form.show()
    app.exec_()


if __name__ == '__main__':
    gl.conn_string = 'host=192.168.0.250 dbname=prism user=root password=masterkey'
    data_sets.get_ds_tecnicos()
    main()
