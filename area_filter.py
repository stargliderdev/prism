#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTableWidget, QApplication, QToolButton, QMessageBox, QLineEdit

import data_sets
import libpg
import qlib as qc
import ex_grid
import parameters as gl


class AreaFilter(QDialog):
    def __init__(self, parent=None):
        super(AreaFilter, self).__init__(parent)
        # self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
        self.resize(400, 600)
        self.setWindowTitle('Zonas')
        self.ret = {'responce': False, 'area_id': 0}
        masterLayout = QVBoxLayout(self)
        self.areaGrid = QTableWidget()
        self.areaGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.areaGrid.setSelectionMode(QTableWidget.MultiSelection)
        self.areaGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.areaGrid.verticalHeader().setDefaultSectionSize(20)
        self.areaGrid.verticalHeader().setVisible(False)
        # self.areaGrid.itemDoubleClicked.connect(self.save_click)
        ex_grid.make_grid(self.areaGrid, ['', 'Zona'], [(1, 250)])
        masterLayout.addWidget(self.areaGrid)
        okBtn = QPushButton('Valida')
        okBtn.clicked.connect(self.ok_click)
        
        cancelBtn = QPushButton('Sair')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        masterLayout.addLayout(qc.addHLayout([okBtn,cancelBtn]))
        self.areas_refresh()

   
    def areas_refresh(self):
        hl = libpg.sql_query(
            '''SELECT area_id, area_name from areas  order by area_name''')
        ex_grid.grid_std(self.areaGrid, data=hl, f_col=['i', 's'])
        self.areaGrid.setColumnWidth(0, 0)

    def cancel_btn_click(self):
        self.close()

    def ok_click(self):
        areas_ids = []
        areas_names = []
        sel = set(index.row() for index in self.areaGrid.selectedIndexes())
        for n in set(sel): # self.areaGrid.selectedIndexes():
            areas_ids.append(int(self.areaGrid.item(n, 0).text()))
            areas_names.append(self.areaGrid.item(n, 1).text())
        self.ret = {'responce': True, 'areas_ids': areas_ids, 'areas_names': areas_names}
        self.close()

def main():
    gl.user_dict = data_sets.get_user_data('jorge', '1697')
    app = QApplication(sys.argv)
    form = AreaFilter()
    form.show()
    app.exec_()
    print(form.ret)


if __name__ == '__main__':
    main()

