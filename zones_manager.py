#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTableWidget, QApplication, QLineEdit, QMessageBox, \
    QInputDialog
from PyQt5.QtCore import Qt
import sys
import libpg
import qlib as qc
import ex_grid


class ZoneManager(QDialog):
    def __init__(self, parent=None):
        super(ZoneManager, self).__init__(parent)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Altera Estado')
        self.ret = (False, '')
        masterLayout = QVBoxLayout(self)
        self.zonesGrid = QTableWidget()
        self.zonesGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.zonesGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.zonesGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.zonesGrid.verticalHeader().setDefaultSectionSize(20)
        self.zonesGrid.verticalHeader().setVisible(False)
        ex_grid.make_grid(self.zonesGrid, ['#','Estado'], col_width=[(0,0),(1, 200)])
        cancelBtn = QPushButton('Sair')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        addZoneBtn = QPushButton('Adiciona')
        addZoneBtn.clicked.connect(self.add_zone)
        masterLayout.addWidget(self.zonesGrid)
        masterLayout.addLayout(qc.addHLayout([addZoneBtn,cancelBtn]))
        self.refresh_grid()
    
    def refresh_grid(self):
        hl = libpg.sql_query('''SELECT area_id, area_name from areas order by area_name ASC''')
        ex_grid.grid_std(self.zonesGrid, data=hl, f_col=['i', 's'])
    
    def cancel_btn_click(self):
        self.ret = (False,'')
        self.close()
        
    def add_zone(self):
        b, ok = QInputDialog.getText(self, "Adicionar Zona", "Zona", QLineEdit.Normal)
        if ok and not b == '':
            libpg.execute_query('insert into areas (area_name, zone_level) values (%s,1)', (b,))
            self.refresh_grid()
        else:
            pass
        
        
def main():
    app = QApplication(sys.argv)
    form = ZoneManager()
    form.show()
    app.exec_()
    print(form.ret)



if __name__ == '__main__':
    main()