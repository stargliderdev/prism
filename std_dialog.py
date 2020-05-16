#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout, QPushButton, QTableWidget, QHBoxLayout

import qlib as qc


class TestClass(QDialog):
    def __init__(self, parent=None):
        super(TestClass, self).__init__(parent)
        self.setWindowTitle('Teste')
        self.resize(1024, 768)
        masterLayout = QVBoxLayout(self)
        buttonLayout = QHBoxLayout()
        self.updateBtn = QPushButton('Actualiza')
        self.updateBtn.clicked.connect(self.update_click)
        
        cancelBtn = QPushButton('Sair')
        cancelBtn.clicked.connect(self.exit)
        
        buttonLayout.addWidget(cancelBtn)
        masterLayout.addLayout(qc.addHLayout([self.updateBtn, True, cancelBtn]))
        self.gridTest = QTableWidget()
        masterLayout.addWidget(self.gridTest)
    
    def update_click(self):
        pass
    
    def exit(self):
        self.close()


def main():
    app = QApplication(sys.argv)
    form = TestClass()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
