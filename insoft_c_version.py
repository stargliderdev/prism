import sys

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QPushButton, QApplication

import ex_grid
import liblogos
import libpg
import parameters as gl
import qlib as qc

class ChangeComercialVersion(QDialog):
    def __init__(self, parent=None):
        super(ChangeComercialVersion, self).__init__(parent)
        self.resize(400, 400)
        self.ret = False, ''
        self.setWindowTitle('Versão Comercial')
        masterLayout = QVBoxLayout(self)
        self.dbms_grd = QTableWidget()
        self.dbms_grd.setSelectionBehavior(QTableWidget.SelectRows)
        self.dbms_grd.setSelectionMode(QTableWidget.SingleSelection)
        self.dbms_grd.setEditTriggers(QTableWidget.NoEditTriggers)
        self.dbms_grd.verticalHeader().setDefaultSectionSize(20)
        self.dbms_grd.setAlternatingRowColors(True)
        self.dbms_grd.setStyleSheet("alternate-background-color: #89CF00;")
        self.dbms_grd.verticalHeader().setVisible(False)
        self.dbms_grd.horizontalHeader().setVisible(False)
        self.dbms_grd.itemDoubleClicked.connect(self.save_click)
        ex_grid.make_grid(self.dbms_grd, ['Sistema e Versão','t',''], [(0, 0),(1,350),(2,0)])
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        masterLayout.addLayout(qc.addHLayout([self.dbms_grd]))
        masterLayout.addLayout(qc.addHLayout([cancelBtn]))
        hl = libpg.sql_query('''select insoft_opt_code, insoft_opt_name from insoft_opt where insoft_opt_level=1 and insoft_opt_active=True order by insoft_opt_order''')
        ex_grid.grid_std(self.dbms_grd, data=hl, f_col=['s','s'])

    def cancel_btn_click(self):
        self.ret = False, '',''
        self.close()
    
    def save_click(self):
        """devolve true se e a chave do registo escolhido"""
        self.ret = True,self.dbms_grd.item(self.dbms_grd.currentRow(), 0).text(),\
                   self.dbms_grd.item(self.dbms_grd.currentRow(), 1).text()
        self.close()
        
        
def main():
    app = QApplication(sys.argv)
    form = ChangeComercialVersion()
    form.show()
    app.exec_()
    print(form.ret)

if __name__ == '__main__':
    pass
