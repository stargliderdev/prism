#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import datetime

from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout, QLineEdit, QPlainTextEdit, QComboBox, \
    QPushButton, QDateTimeEdit

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
        self.ddns_text = data_dict['proc_report_internal']
        self.client_name = QLineEdit()
        self.addInfoEdt = QPlainTextEdit()
        self.techCbx = QComboBox()
        closeBtn = QPushButton('Fecha')
        closeBtn.clicked.connect(self.close_click)
        pendingBtn = QPushButton('Pendente')
        pendingBtn.clicked.connect(self.pending_click)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_click)
        
        masterLayout.addLayout(qc.addHLayout(['Técnico', self.techCbx]))
        masterLayout.addLayout(qc.addHLayout(['Quem', self.client_name]))
        self.proc_duracao = QDateTimeEdit()
        self.proc_duracao.setMaximumWidth(80)
        self.proc_duracao.setDisplayFormat("hh:mm")
        # date_object = datetime.datetime.strptime('00:04:00', "%H:%M:%S")
        duration = (datetime.datetime.now() - gl.date_time_stack) + datetime.timedelta(seconds=220)
        a = str(duration).split(':')
        dd = datetime.datetime(1900,1,1,int(a[0]),int(a[1]), int(a[2][:2]))
        self.proc_duracao.setDateTime(dd)
        masterLayout.addLayout(qc.addHLayout(['Duração', self.proc_duracao, True]))
        masterLayout.addLayout(qc.addVLayout(['Info Adicional', self.addInfoEdt]))
        masterLayout.addLayout(qc.addHLayout([pendingBtn, closeBtn, cancelBtn]))
        
        self.techCbx.addItems(gl.ds_tecnicos)
        
        self.client_name.setText(data_dict['proc_quem'])
        self.addInfoEdt.setPlainText(data_dict['proc_reported'])
        self.techCbx.setCurrentText(data_dict['proc_tecnico'])
    
    def close_click(self):
        self.ret = (True, {'proc_tecnico': self.techCbx.currentText(), 
                           'proc_quem': self.client_name.text(),
                           'proc_report_internal': self.addInfoEdt.toPlainText() + '\n' + self.ddns_text,
                           'proc_duracao': str(self.proc_duracao.dateTime().toPyDateTime().hour) + ':' + str(self.proc_duracao.dateTime().toPyDateTime().minute)
                           })
        self.close()
    
    def pending_click(self):
        self.ret = (True, {'proc_tecnico': self.techCbx.currentText(),
                           'proc_quem': self.client_name.text(),
                           'proc_report_internal': self.addInfoEdt.toPlainText() + '\n' + self.ddns_text,
                           'proc_duracao': str(self.proc_duracao.dateTime().toPyDateTime().hour) + ':' + str(self.proc_duracao.dateTime().toPyDateTime().minute),
                           'proc_pendente': True,
                           'proc_status': 'Pendente de Intervenção'
                           })
        self.close()
        
    def cancel_click(self):
        self. ret = (False,)
        self.close()

def main():
    app = QApplication(sys.argv)
    form = AddInfo()
    form.show()
    app.exec_()


if __name__ == '__main__':
    gl.conn_string = 'host=192.168.0.250 dbname=prism user=root password=masterkey'
    data_sets.get_ds_tecnicos()
    main()
