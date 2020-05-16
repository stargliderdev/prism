#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QApplication, QStyleFactory, QDesktopWidget
from PyQt5.QtCore import Qt
import sys

import liblogos
import qlib as ql
import parameters as gl

class Dialog(QDialog):
    def __init__(self, title, err,sql, data,  parent = None):
        super(Dialog,  self).__init__(parent)
        self.resize(800, 600)
        # self.center()
        msg = '<br><br><font color=”#E30022”>Copia o erro e comunica!</font>'
        self.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.WindowTitleHint)
        self.setWindowTitle(title)
        masterLayout = QVBoxLayout(self)

        outputerror = QTextEdit()
        outputerror.setHtml('Erro:<br><strong>' + err + '<br></strong>SQL:<br>' + sql + '<br>' + str(data) + '<br><br>' + msg)
        masterLayout.addWidget(outputerror)
        self.exit = QPushButton('Sair')
        # self.connect(self.exit, SIGNAL("clicked()"), self.quit)
        self.exit.clicked.connect(self.quit)
        
        masterLayout.addLayout(ql.addHLayout([self.exit]))
        QApplication.setStyle(QStyleFactory.create('plastique'))
        liblogos.log_actions(gl.user_dict, 'sql error', err + '\n' + sql)


    def quit(self):
        sys.exit(1)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':
    pass