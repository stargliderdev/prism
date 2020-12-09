#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QTableWidget, QPushButton, QHBoxLayout,QApplication, QToolButton,  QMessageBox
from PyQt5.QtCore import Qt
import sys

# from qtconsole.qt import QtCore

import ex_grid
import libpg
import qlib as qc
import models_lib


class BrandsBrowser(QDialog):
    def __init__(self, parent=None):
        super(BrandsBrowser, self).__init__(parent)
        self.setWindowTitle('Marcas')
        masterLayout = QVBoxLayout(self)
        self.tag_list = ''
        self.ret = {'brand_id': 0, 'brand_name': ''}
        self.searchEdit = QLineEdit()
        self.searchEdit.setMaximumWidth(250)
        self.searchEdit.textChanged.connect(self.brand_search_changed)
        masterLayout.addWidget(self.searchEdit)
        gridContainLayout = QHBoxLayout()
        self.brandsGrid = QTableWidget()
        self.brandsGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.brandsGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.brandsGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.brandsGrid.verticalHeader().setDefaultSectionSize(20)
        self.brandsGrid.verticalHeader().setVisible(False)
        self.brandsGrid.resizeColumnsToContents()
        self.brandsGrid.setMaximumWidth(250)
        self.brandsGrid.setAlternatingRowColors(True)
        self.brandsGrid.setStyleSheet("alternate-background-color: #e6f2ff;")
        self.brandsGrid.itemDoubleClicked.connect(self.brands_validate)
        addBrand = QToolButton()
        addBrand.setText('+')
        addBrand.clicked.connect(self.brands_add_click)
        removeBrand = QToolButton()
        removeBrand.setText('-')
        removeBrand.clicked.connect(self.brand_deactivate_click)
        dum1Layout = QVBoxLayout()
        dum1Layout.addWidget(self.brandsGrid)
        dum1Layout.addLayout(qc.addHLayout([addBrand,removeBrand, True]))
        gridContainLayout.addLayout(dum1Layout)
        masterLayout.addLayout(gridContainLayout)
        exit_btn = QPushButton('Sair')
        exit_btn.clicked.connect(self.exit_click)
        masterLayout.addWidget(exit_btn)
        self.brands_refresh()
    
    def brands_validate(self):
        b = int(self.brandsGrid.item(self.brandsGrid.currentRow(), 0).text())
        b_name = self.brandsGrid.item(self.brandsGrid.currentRow(), 1).text()
        self.ret = {'brand_id': b, 'brand_name': b_name}
        self.close()
   
    def brands_refresh(self):
        self.c_grid = 10
        sql = '''select br_id,br_name from brands where br_active = True order by br_name '''
        dataset = libpg.query_many(sql, True)
        ex_grid.ex_grid_update(self.brandsGrid, {0: ['ID', 'i'], 1: ['Marca', 's']}, dataset, hidden=0)
        # self.brandsGrid.horizontalHeader().setVisible(False)
        self.brandsGrid.setColumnWidth(0, 80)
        self.brandsGrid.setColumnWidth(1, 200)
    
    def brand_search_changed(self, text):
        search = '\'' + str(text).lower() + '%%\''
        sql = '''select br_id, br_name from brands where lower(br_name) like ''' + search + ''' order by br_name'''
        dataset = libpg.query_many(sql, True)
        ex_grid.ex_grid_update(self.brandsGrid, {0: ['ID', 'i'], 1: ['Nome', 's']}, dataset, hidden=0)
    
    def brands_add_click(self):
        form = models_lib.AddBrand()
        form.exec_()
        self.brands_refresh()
    
    def brand_deactivate_click(self):
        pass
    
    def exit_click(self):
        self.close()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            pass


def main():
    app = QApplication(sys.argv)
    cf = {'mode': 0}
    form = BrandsBrowser(cf)
    form.show()
    app.exec_()
    print(form.ret)


if __name__ == '__main__':
    main()