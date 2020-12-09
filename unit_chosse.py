#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog,QVBoxLayout,QPushButton,QTableWidget
from PyQt5.QtCore import Qt
import libpg
import qlib as qc
import ex_grid


class UnitChoseDialog(QDialog):
    def __init__(self, units_list, parent=None):
        super(UnitChoseDialog, self).__init__(parent)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
        self.resize(400, 400)
        self.setWindowTitle('Escolhe a Unidade')
        self.ret = (False, '')
        masterLayout = QVBoxLayout(self)
        self.unitsContactGrid = QTableWidget()
        self.unitsContactGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.unitsContactGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.unitsContactGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.unitsContactGrid.verticalHeader().setDefaultSectionSize(20)
        self.unitsContactGrid.verticalHeader().setVisible(False)
        self.unitsContactGrid.itemDoubleClicked.connect(self.save_click)
        ex_grid.make_grid(self.unitsContactGrid, ['id','Estado'], [(0,0),(1, 360)])
        self.unitsContactGrid.horizontalHeader().setVisible(False)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        masterLayout.addWidget(self.unitsContactGrid)
        masterLayout.addLayout(qc.addHLayout([cancelBtn]))
        ex_grid.grid_std(self.unitsContactGrid, data=units_list, f_col=['i', 's'])
        self.unitsContactGrid.setColumnWidth(0, 0)
    
    def cancel_btn_click(self):
        self.ret = (False,'')
        self.close()
    
    def save_click(self):
        self.ret = (True,
                    int(self.unitsContactGrid.item(self.unitsContactGrid.currentRow(), 0).text()),
                    self.unitsContactGrid.item(self.unitsContactGrid.currentRow(), 1).text())
        self.close()
        
        
if __name__ == '__main__':
    pass