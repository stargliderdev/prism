#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTableWidget
from PyQt5.QtCore import Qt
import libpg
import qlib as qc
import ex_grid


class UnitTypeBrowser(QDialog):
    def __init__(self, parent=None):
        super(UnitTypeBrowser, self).__init__(parent)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Altera Estado')
        self.ret = (False, '')
        masterLayout = QVBoxLayout(self)
        self.hwUnitType = QTableWidget()
        self.hwUnitType.setSelectionBehavior(QTableWidget.SelectRows)
        self.hwUnitType.setSelectionMode(QTableWidget.SingleSelection)
        self.hwUnitType.setEditTriggers(QTableWidget.NoEditTriggers)
        self.hwUnitType.verticalHeader().setDefaultSectionSize(20)
        self.hwUnitType.verticalHeader().setVisible(False)
        self.hwUnitType.itemDoubleClicked.connect(self.save_click)
        ex_grid.make_grid(self.hwUnitType, ['Estado'], [(0, 180)])
        self.hwUnitType.horizontalHeader().setVisible(False)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        masterLayout.addLayout(qc.addHLayout([self.hwUnitType, True]))
        masterLayout.addLayout(qc.addHLayout([cancelBtn]))
        hl = libpg.sql_query('''SELECT un_type_id, un_type_name from unit_type order by un_type_name ASC''')
        ex_grid.grid_std(self.hwUnitType, data=hl, f_col=['i', 's'])
        self.hwUnitType.setColumnWidth(0, 0)
        self.hwUnitType.setColumnWidth(1, 250)
    
    def cancel_btn_click(self):
        self.ret = (False, '')
        self.close()
    
    def save_click(self):
        self.ret = (True, self.hwUnitType.item(self.hwUnitType.currentRow(), 1).text(),
                    int(self.hwUnitType.item(self.hwUnitType.currentRow(), 0).text()))
        self.close()


if __name__ == '__main__':
    pass