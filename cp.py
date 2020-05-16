#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QToolButton, QMessageBox, QTableWidget
from PyQt5.QtGui import QIcon

import libpg
import ex_grid
import qlib as qc


class CpSearch(QDialog):
    def __init__(self,cp_list=[], parent=None):
        super(CpSearch, self).__init__(parent)
        masterLayout = QVBoxLayout(self)
        self.resize(800, 400)
        self.ret = (False, '')
        self.saveBtn = QPushButton('Valida')
        self.saveBtn.clicked.connect(self.save_click)
        
        self.cancelBtn = QPushButton('Cancela')
        self.cancelBtn.clicked.connect(self.exit_click)
        
        masterLayout.addLayout(qc.addHLayout([self.saveBtn, True, self.cancelBtn]))
        self.postalCodeMainEdt = QLineEdit()
        self.postalCodeMainEdt.setMaximumWidth(60)
        self.postalCodeLowEdt = QLineEdit()
        self.postalCodeLowEdt.setMaximumWidth(40)
        search_cp_Btn = QToolButton()
        search_cp_Btn.setToolTip('Pesquisa')
        search_cp_Btn.setIcon(QIcon('.//img//search_tags.png'))
        masterLayout.addLayout(qc.addHLayout(['Código Postal', self.postalCodeMainEdt, self.postalCodeLowEdt,search_cp_Btn,True], lw=160))
        search_cp_Btn.clicked.connect(self.search_cp_click)
        self.postalCodeMainEdt.returnPressed.connect(self.search_cp_click)
        
        self.setWindowTitle('Pesquisa de Códigos Postais')
        self.cp_grid = QTableWidget()
        self.cp_grid.itemDoubleClicked.connect(self.save_click)
        
        self.cp_grid.setSelectionBehavior(QTableWidget.SelectRows)
        self.cp_grid.setSelectionMode(QTableWidget.SingleSelection)
        self.cp_grid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cp_grid.verticalHeader().setDefaultSectionSize(20)
        self.cp_grid.setAlternatingRowColors(True)
        self.cp_grid.setStyleSheet("alternate-background-color: #BFFF80;")
        self.cp_grid.verticalHeader().setVisible(False)
        ex_grid.make_grid(self.cp_grid, ['Rua', 'Código Postal', 'Localidade'], [(0, 300), (1, 270), (2, 270)])
        masterLayout.addWidget(self.cp_grid)
        self.postalCodeMainEdt.setFocus()
        if not cp_list == []:
            self.postalCodeMainEdt.setText(cp_list[0])
            self.postalCodeLowEdt.setText(cp_list[1])
        
    def search_cp_click(self):
        high = self.postalCodeMainEdt.text().zfill(4)
        low = self.postalCodeLowEdt.text().zfill(3)
        try:
            high = int(high)
        except ValueError:
            self.postalCodeMainEdt.setText('erro')
            high = '0000'
        try:
            low = int(low)
        except ValueError:
            self.postalCodeLowEdt.setText('ERR')
            low = '000'
        sql = '''select cp_rua, cp_num||'-'||LPAD(cp_ext::text, 3, '0')||' ' ||cp_desig, cp_localidade
                         from codigos_postais where cp_num =''' + str(high) + ''' and cp_ext=''' + str(low)
        hl = libpg.sql_query(sql)
        ex_grid.grid_std(self.cp_grid, data=hl, f_col=['s', 's', 's'])
        if self.cp_grid.rowCount() == 0:
            QMessageBox.critical(None,"Mensagem","Código Postal não encontrado")

                    
    def save_click(self):
        if self.cp_grid.rowCount() > 0 and self.cp_grid.currentRow() > -1:
            self.ret = (True, self.cp_grid.item(self.cp_grid.currentRow(), 0).text(),
                        self.cp_grid.item(self.cp_grid.currentRow(), 1).text(),
                        self.cp_grid.item(self.cp_grid.currentRow(), 2).text())
            self.close()
    
    def exit_click(self):
        self.close()


# def main():
#     app = QApplication(sys.argv)
#     form = CpSearch()
#     form.show()
#     app.exec_()


if __name__ == '__main__':
    pass
