#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QButtonGroup, QApplication, \
    QTableWidget
from PyQt5.QtCore import Qt
import ex_grid
import libpg
import parameters as gl
import qlib as qc

class ProcessEndDialog(QDialog):
    def __init__(self, parent=None):
        super(ProcessEndDialog, self).__init__(parent)
        self.setWindowTitle('Estado do Pedido')
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
        self.resize(800, 600)
        self.setWindowTitle('Escolhe a Unidade')
        self.ret = (False, '')
        masterLayout = QVBoxLayout(self)
        self.unitsContactGrid = QTableWidget()
        self.unitsContactGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.unitsContactGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.unitsContactGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        # self.unitsContactGrid.verticalHeader().setVisible(False)
        self.unitsContactGrid.itemDoubleClicked.connect(self.save_click)
        ex_grid.make_grid(self.unitsContactGrid, ['id', 'Estado'], [(0, 0), (1, 360)])
        self.unitsContactGrid.verticalHeader().setDefaultSectionSize(10)
        self.unitsContactGrid.horizontalHeader().setVisible(False)
        self.priceTableGrid = QTableWidget()
        
        masterLayout.addLayout(qc.addHLayout([self.unitsContactGrid,self.priceTableGrid]))
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        # masterLayout.addWidget(self.unitsContactGrid)
        masterLayout.addLayout(qc.addHLayout([cancelBtn]))
        ex_grid.grid_std(self.unitsContactGrid, data=self.get_data(), f_col=['i', 's'])
        self.unitsContactGrid.setColumnWidth(0, 0)

    def get_data(self):
        a = libpg.query_many('''select st_id, st_descricao
                    from status  order by st_sort       ''',
                             (True,))
        return a

    def cancel_btn_click(self):
        self.ret = (False, '')
        self.close()

    def save_click(self):
        self.ret = (True,
                    int(self.unitsContactGrid.item(self.unitsContactGrid.currentRow(), 0).text()),
                    self.unitsContactGrid.item(self.unitsContactGrid.currentRow(), 1).text())
        self.close()
        
def main():
    app = QApplication(sys.argv)
    form = ProcessEndDialog()
    form.show()
    app.exec_()


if __name__ == '__main__':
    gl.conn_string = 'host=192.168.0.250 dbname=prism user=root password=masterkey'
    main()