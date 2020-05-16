#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout, QPushButton, QTableWidget, QHBoxLayout

import ex_grid
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
        self.gridTest.itemDoubleClicked.connect(self.grid_click)
        self.gridTest.setSelectionBehavior(QTableWidget.SelectRows)
        self.gridTest.setSelectionMode(QTableWidget.SingleSelection)
        self.gridTest.setEditTriggers(QTableWidget.NoEditTriggers)
        self.gridTest.verticalHeader().setDefaultSectionSize(20)
        self.gridTest.setAlternatingRowColors(True)
        self.gridTest.setStyleSheet("alternate-background-color: #f5f5f0;")
        self.gridTest.verticalHeader().setVisible(False)
        ex_grid.make_grid(self.gridTest, ['ctt_id', 'unit', '', 'Nome', 'Contacto', 'Tipo', 'tp'],
                          [(0, 20), (1, 20), (2, 25), (3, 160), (4, 260), (5, 200), (6, 20)])

        masterLayout.addWidget(self.gridTest)
        self.grid_refresh()
    
    def update_click(self):
        pass
    
    def grid_click(self):
        print(int(self.gridTest.item(self.gridTest.currentRow(), 0).text()))
    
    def grid_refresh(self):
        hl = [(1,1,'a','b','c','d',99)]
        ex_grid.grid_std(self.gridTest, data=hl, f_col=['i', 'i', 's', 's', 's', 's', 'i'])
    
    def exit(self):
        self.close()


def main():
    app = QApplication(sys.argv)
    form = TestClass()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
