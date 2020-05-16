#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout, QLineEdit, QPlainTextEdit, QComboBox, \
    QPushButton

import data_sets
import qlib as qc
import parameters as gl


class AddInfo(QDialog):
    def __init__(self, parent=None):
        super(AddInfo, self).__init__(parent)
        masterLayout = QVBoxLayout(self)
        self.resize(600, 400)
        self.setWindowTitle('Adiciona informação ao Pedido')
        self.client_name = QLineEdit()
        self.addInfoEdt = QPlainTextEdit()
        self.techCbx = QComboBox()
        okBtn = QPushButton('Continua')
        cancelBtn = QPushButton('Cancela')
        
        masterLayout.addLayout(qc.addHLayout(['Técnico', self.techCbx]))
        masterLayout.addLayout(qc.addHLayout(['Quem', self.client_name]))
        masterLayout.addLayout(qc.addVLayout(['Info Adicional', self.addInfoEdt]))
        masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
        
        self.techCbx.addItems(gl.ds_tecnicos)
        okBtn.clicked.connect(self.ok_click)
        cancelBtn.clicked.connect(self.cancel_click)
    
    def ok_click(self):
        self.ret = (True, {'tech': self.techCbx.currentText(), 'client_name': self.client_name.text(),
                           'add_info': self.addInfoEdt.toPlainText()})
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
