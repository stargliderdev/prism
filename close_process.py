#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QApplication, QComboBox

import data_sets
import libpg
import parameters as gl
import qlib as qc


class CloseProcess(QDialog):
    def __init__(self, parent=None):
        """ fecha o processo ou não"""
        super(CloseProcess, self).__init__(parent)
        self.setWindowTitle('Estado do Pedido')
        self.resize(800, 600)
        mainLayout = QVBoxLayout(self)
        self.procActionCBox = QComboBox()
        self.procActionCBox.addItems(gl.proc_action)
        mainLayout.addLayout(qc.addHLayout(['Accção', self.procActionCBox]))
        # butoes
        validBtn = QPushButton('Validar')
        cancelBtn = QPushButton('Cancelar')
        # self.setSizes(self.closeBtn)
        cancelBtn.clicked.connect(self.closeBtn_click)
        mainLayout.addStretch()
        mainLayout.addLayout(qc.addHLayout([validBtn, cancelBtn]))
    
    def button_group_click(self, btn):
        # # 0 tem o nome da acção e o 1 tem a accção
        self.toto = btn.text()
        self.close()
    
    def closeBtn_click(self):
        self.toto = -1
        self.close()
    
def main():
    data_sets.get_proc_close_action()
    app = QApplication(sys.argv)
    form = CloseProcess()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
