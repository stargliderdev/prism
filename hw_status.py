#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog,QVBoxLayout,QPushButton,QTableWidget
from PyQt5.QtCore import Qt
import libpg
import qlib as qc
import ex_grid


class HardwareStatus(QDialog):
    def __init__(self, parent=None):
        super(HardwareStatus, self).__init__(parent)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Altera Estado')
        self.ret = (False, '')
        masterLayout = QVBoxLayout(self)
        self.hwStatusGrid = QTableWidget()
        self.hwStatusGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.hwStatusGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.hwStatusGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.hwStatusGrid.verticalHeader().setDefaultSectionSize(20)
        self.hwStatusGrid.verticalHeader().setVisible(False)
        self.hwStatusGrid.itemDoubleClicked.connect(self.save_click)
        ex_grid.make_grid(self.hwStatusGrid, ['Unidades'], [(0, 160)])
        self.hwStatusGrid.horizontalHeader().setVisible(False)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        masterLayout.addLayout(qc.addHLayout([self.hwStatusGrid, True]))
        masterLayout.addLayout(qc.addHLayout([cancelBtn]))
        hl = libpg.sql_query('''SELECT hwd_status_id, hwd_status_name from hw_status order by hwd_status_name ASC''')
        ex_grid.grid_std(self.hwStatusGrid, data=hl, f_col=['i','s'])
        self.hwStatusGrid.setColumnWidth(0,0)
    
    def cancel_btn_click(self):
        self.ret = (False,'')
        self.close()
    
    def save_click(self):
        self.ret = (True, self.hwStatusGrid.item(self.hwStatusGrid.currentRow(), 1).text(), int(self.hwStatusGrid.item(self.hwStatusGrid.currentRow(), 0).text()))
        self.close()
        
        
if __name__ == '__main__':
    pass