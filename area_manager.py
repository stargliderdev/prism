#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTableWidget, QApplication, QToolButton, QMessageBox, QLineEdit

import data_sets
import libpg
import qlib as qc
import ex_grid
import parameters as gl


class AreaManager(QDialog):
    def __init__(self, parent=None):
        super(AreaManager, self).__init__(parent)
        # self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
        self.resize(400, 600)
        self.setWindowTitle('Zonas')
        self.ret = {'responce': False, 'area_id': 0}
        masterLayout = QVBoxLayout(self)
        self.areaGrid = QTableWidget()
        self.areaGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.areaGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.areaGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.areaGrid.verticalHeader().setDefaultSectionSize(20)
        self.areaGrid.verticalHeader().setVisible(False)
        self.areaGrid.itemDoubleClicked.connect(self.save_click)
        ex_grid.make_grid(self.areaGrid, ['', 'Zona'], [(1, 250)])
        masterLayout.addWidget(self.areaGrid)
        addArea = QToolButton()
        addArea.setText('+')
        addArea.clicked.connect(self.area_add_click)
        removeBrand = QToolButton()
        removeBrand.setText('-')
        dum1Layout = QVBoxLayout()
        dum1Layout.addLayout(qc.addHLayout([addArea, removeBrand, True]))
        masterLayout.addLayout(dum1Layout)
        cancelBtn = QPushButton('Sair')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        masterLayout.addLayout(qc.addHLayout([cancelBtn]))
        self.areas_refresh()

    def area_add_click(self):
        form = AddArea()
        form.exec_()
        self.areas_refresh()
    
    def areas_refresh(self):
        hl = libpg.sql_query(
            '''SELECT area_id, area_name from areas  order by area_name''')
        ex_grid.grid_std(self.areaGrid, data=hl, f_col=['i', 's'])
        self.areaGrid.setColumnWidth(0, 0)
    
    def cancel_btn_click(self):
        # self.ret = (False, '')
        self.close()
    
    def save_click(self):
        self.ret = {'responce': True, 'area_id': int(self.areaGrid.item(self.areaGrid.currentRow(), 0).text()),
                    'area_name': self.areaGrid.item(self.areaGrid.currentRow(), 1).text()}
        self.close()


class AddArea(QDialog):
    def __init__(self, parent=None):
        super(AddArea, self).__init__(parent)
        self.setWindowTitle('Adiciona Zona')
        masterLayout = QVBoxLayout(self)
        self.text_1 = QLineEdit()
        masterLayout.addLayout(qc.addHLayout(['Zona', self.text_1, True], lw=100))
        ok_Btn = QPushButton('Adiciona')
        ok_Btn.clicked.connect(self.save_click)
        cancela_Btn = QPushButton('Cancela')
        cancela_Btn.clicked.connect(self.cancel_btn_click)
        masterLayout.addLayout(qc.addHLayout([ok_Btn, cancela_Btn]))
    
    def cancel_btn_click(self):
        self.close()
    
    def save_click(self):
        a = libpg.query_one('select area_name from areas where lower(area_name)= %s', (self.text_1.text().lower(),))
        if a is None:
            libpg.execute_query('insert into areas (area_name) VALUES (%s)', (str(self.text_1.text()),))
            data_sets.get_ds_areas()
            self.close()
        else:
            QMessageBox.warning(None, "Zona Duplicada", "Esta Zona já existe!")



def main():
    gl.user_dict = data_sets.get_user_data('jorge', '1697')
    app = QApplication(sys.argv)
    form = AreaManager()
    form.show()
    app.exec_()
    print(form.ret)


if __name__ == '__main__':
    main()