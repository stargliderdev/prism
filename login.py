#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton,QMessageBox,QLabel
import sys

import parameters as gl
import qlib as qc
import data_sets
import liblogos


class Login(QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.setWindowTitle('Login')
        masterLayout = QVBoxLayout(self)
        gl.user_dict = {'user_id': 0}
        self.count = 0
        self.user_edt = QLineEdit()
        self.user_password = QLineEdit()
        self.user_password.setEchoMode(1)
        masterLayout.addLayout(qc.addHLayout(['Utilizador',self.user_edt, True], lw=180))
        masterLayout.addLayout(qc.addHLayout(['Password',self.user_password, True], lw=180))
        okBtn = QPushButton('Valida')
        okBtn.clicked.connect(self.save_click)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        
        masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
        infoLabel = QLabel()
        infoLabel.setStyleSheet("color: #00a0ff;")
        infoLabel.setText(gl.db_database.lower() + '@' + gl.db_host + ' ' + gl.VERSION)
        masterLayout.addWidget(infoLabel)
        
    def cancel_btn_click(self):
        sys.exit(1)
    
    def save_click(self):
        gl.user_dict = data_sets.get_user_data(self.user_edt.text(), self.user_password.text())
        if gl.user_dict is None:
            QMessageBox.warning(None,"Erro de autenticação","Utilizador ou password errados! ")
            self.user_password.clear()
            self.count += 1
            if self.count > 3:
                sys.exit(1)
        else:
            liblogos.log_actions(gl.user_dict,'login')
            self.close()
     
if __name__ == '__main__':
    pass
