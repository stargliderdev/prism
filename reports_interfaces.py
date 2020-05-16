#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTableWidget, QApplication
from PyQt5.QtCore import Qt
import libpg
import qlib as qc
import ex_grid


class ReportInterface(QDialog):
    def __init__(self, parent=None):
        super(ReportInterface, self).__init__(parent)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Relatórios')
        self.ret = {'responce': False, 'report_id': 0}
        masterLayout = QVBoxLayout(self)
        self.reportsGrid = QTableWidget()
        self.reportsGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.reportsGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.reportsGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.reportsGrid.verticalHeader().setDefaultSectionSize(20)
        self.reportsGrid.verticalHeader().setVisible(False)
        self.reportsGrid.itemDoubleClicked.connect(self.save_click)
        ex_grid.make_grid(self.reportsGrid, ['', 'Relatório'], [(1, 250)])
        # self.reportsGrid.horizontalHeader().setVisible(False)
        cancelBtn = QPushButton('Sair')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        masterLayout.addLayout(qc.addHLayout([self.reportsGrid, True]))
        masterLayout.addLayout(qc.addHLayout([cancelBtn]))
        hl = libpg.sql_query('SELECT report_id, report_name FROM reports WHERE report_visible=True order by report_order')
        ex_grid.grid_std(self.reportsGrid, data=hl, f_col=['i', 's'])
        self.reportsGrid.setColumnWidth(0, 0)
    
    def cancel_btn_click(self):
        # self.ret = (False, '')
        self.close()
    
    def save_click(self):
        self.ret = {'responce':True, 'report_id': int(self.reportsGrid.item(self.reportsGrid.currentRow(), 0).text()),
                    'report_name': self.reportsGrid.item(self.reportsGrid.currentRow(), 1).text()}
        self.close()


def main():
    app = QApplication(sys.argv)
    form = ReportInterface()
    form.show()
    app.exec_()
    print(form.ret)


if __name__ == '__main__':
    main()
