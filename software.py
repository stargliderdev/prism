#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QTableWidget, QApplication, QInputDialog
import libpg
import qlib as qc
import ex_grid


class SoftwareBrowser(QDialog):
    def __init__(self, unit_dict, parent=None):
        super(SoftwareBrowser, self).__init__(parent)
        self.resize(600, 400)
        self.setWindowTitle('Altera Software')
        masterLayout = QVBoxLayout(self)
        self.software_dict = unit_dict
        self.ret = (False,)
        self.softwareGrid = QTableWidget()
        self.softwareGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.softwareGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.softwareGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.softwareGrid.verticalHeader().setDefaultSectionSize(20)
        self.softwareGrid.setAlternatingRowColors(True)
        self.softwareGrid.setStyleSheet("alternate-background-color: #f2ffcc;")
        self.softwareGrid.verticalHeader().setVisible(False)
        self.softwareGrid.itemDoubleClicked.connect(self.version_refresh)
        ex_grid.make_grid(self.softwareGrid, ['id', 'Marca'], [(0, 0), (1, 160)])
        self.version_grd = QTableWidget()
        self.version_grd = QTableWidget()
        self.version_grd.setSelectionBehavior(QTableWidget.SelectRows)
        self.version_grd.setSelectionMode(QTableWidget.SingleSelection)
        self.version_grd.setEditTriggers(QTableWidget.NoEditTriggers)
        self.version_grd.verticalHeader().setDefaultSectionSize(20)
        self.version_grd.setAlternatingRowColors(True)
        self.version_grd.setStyleSheet("alternate-background-color: #fff5e6;")
        self.version_grd.verticalHeader().setVisible(False)
        self.version_grd.itemDoubleClicked.connect(self.save_click)
        ex_grid.make_grid(self.version_grd, ['id', 'Versão','free'], [(0, 0), (1, 160),(2,0)])
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        
        masterLayout.addLayout(qc.addHLayout([self.softwareGrid, self.version_grd]))
        masterLayout.addLayout(qc.addHLayout([cancelBtn]))
        self.software_refresh()
     
    def software_refresh(self):
        f = ' sft_active = True and sft_software_type  =' + str(self.software_dict['unit_type'])
        if self.software_dict['unit_type'] == 0:
            f = ' sft_software_type >0'
        sql = '''SELECT sft_id, sft_software
                    from software_type
                    where  ''' + f + ''' order by sft_sort ASC'''
        hl = libpg.query_many(sql)
        ex_grid.grid_std(self.softwareGrid, data=hl, f_col=['i', 's'])
    
    def version_refresh(self):
        sft_id = int(self.softwareGrid.item(self.softwareGrid.currentRow(), 0).text())
        f = ''' sversion_active= True and sversion_software_id=''' + str(sft_id)
        if self.software_dict['unit_type'] == 0:
            f = ''' sversion_software_id=''' + str(sft_id)
        sql = '''SELECT sversion_id, sversion_name, cast(sversion_free as TEXT)
                 from software_version
                 where  ''' + f + '''  order by sversion_name DESC'''
        hl = libpg.query_many(sql)
        ex_grid.grid_std(self.version_grd, data=hl, f_col=['i', 's','s'])
    
    def cancel_btn_click(self):
        self.ret = (False, '')
        self.close()
    
    def save_click(self):
        if self.version_grd.item(self.version_grd.currentRow(), 2).text() == 'true':
            b, ok = QInputDialog.getText(self, self.tr("Versão"), self.tr("Versão Livre"), QLineEdit.Normal)
            if ok and not b == '':
                self.ret = (True, self.softwareGrid.item(self.softwareGrid.currentRow(), 1).text(),
                            b,
                            int(self.softwareGrid.item(self.softwareGrid.currentRow(), 0).text()))
            self.close()
        else:
            self.ret = (True, self.softwareGrid.item(self.softwareGrid.currentRow(), 1).text(),
                        self.version_grd.item(self.version_grd.currentRow(), 1).text(),
                        int(self.softwareGrid.item(self.softwareGrid.currentRow(), 0).text()))
            self.close()
        

def main():
    app = QApplication(sys.argv)
    form = SoftwareBrowser(1)
    form.show()
    app.exec_()
    print(form.ret)


if __name__ == '__main__':
    main()
