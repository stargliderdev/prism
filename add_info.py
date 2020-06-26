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
        self.client_name = QLineEdit()
        self.addInfoEdt = QPlainTextEdit()
        self.techCbx = QComboBox()
        okBtn = QPushButton('Continua')
        cancelBtn = QPushButton('Cancela')
        
        masterLayout.addLayout(qc.addHLayout(['Técnico', self.techCbx]))
        masterLayout.addLayout(qc.addHLayout(['Quem', self.client_name]))
        self.proc_duracao = QDateTimeEdit()
        self.proc_duracao.setMaximumWidth(80)
        self.proc_duracao.setDisplayFormat("hh:mm")
        date_object = datetime.datetime.strptime('00:04:00', "%H:%M:%S")
        self.proc_duracao.setDateTime(date_object)
        masterLayout.addLayout(qc.addHLayout(['Duração', self.proc_duracao, True]))
        masterLayout.addLayout(qc.addVLayout(['Info Adicional', self.addInfoEdt]))
        masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
        
        self.techCbx.addItems(gl.ds_tecnicos)
        okBtn.clicked.connect(self.ok_click)
        cancelBtn.clicked.connect(self.cancel_click)
        
        self.client_name.setText(data_dict['proc_quem'])
        self.addInfoEdt.setPlainText(data_dict['proc_reported'])
        self.techCbx.setCurrentText(data_dict['proc_tecnico'])
    
    def ok_click(self):
        self.ret = (True, {'proc_tecnico': self.techCbx.currentText(), 
                           'proc_quem': self.client_name.text(),
                           'proc_reported': self.addInfoEdt.toPlainText(), 
                           'proc_duracao': str(self.proc_duracao.dateTime().toPyDateTime().hour) + ':' + str(self.proc_duracao.dateTime().toPyDateTime().minute)
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
