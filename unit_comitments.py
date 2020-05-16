#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QLabel, QCheckBox, QVBoxLayout, QLineEdit, QTabWidget, QPushButton, \
    QWidget, QToolButton, QDateEdit, QTextEdit, QMessageBox, QCalendarWidget, QDesktopWidget, QTableWidget, QComboBox, \
    QInputDialog
from PyQt5.QtCore import Qt

import classes_un
import liblogos
import libpg
import ex_grid
import unit_setup
import parameters as gl


class AddCommitBrowser(QDialog):
    def __init__(self, unit_id=0, unit_type=0, parent=None):
        super(AddCommitBrowser, self).__init__(parent)
        masterLayout = QVBoxLayout(self)
        self.unit_id = unit_id
        self.unit_type = unit_type
        self.resize(600, 300)
        self.setWindowTitle('Adiciona compromissos')
        self.commit_grid = QTableWidget()
        self.commit_grid.itemDoubleClicked.connect(self.add_commit_click)
        
        self.commit_grid.setSelectionBehavior(QTableWidget.SelectRows)
        self.commit_grid.setSelectionMode(QTableWidget.SingleSelection)
        self.commit_grid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.commit_grid.verticalHeader().setDefaultSectionSize(20)
        self.commit_grid.setAlternatingRowColors(True)
        self.commit_grid.setStyleSheet("alternate-background-color: #89CFF0;")
        self.commit_grid.verticalHeader().setVisible(False)
        
        ex_grid.make_grid(self.commit_grid, ['ct_id', 'Nome'], [(0, 0), (1, 270)])
        masterLayout.addWidget(self.commit_grid)
        sql = '''select cmt_id, cmt_name
            from unit_types_ref, comit_types
            where un_type_ref_class=1 and un_type_ref_unit_type = %s and un_type_ref_setting_id=comit_types.cmt_id;'''
        hl = libpg.query_many(sql, (unit_type,))
        ex_grid.grid_std(self.commit_grid, data=hl, f_col=['i', 's'])
    
    def add_commit_click(self):
        self.close()
        self.cmt_type = int(self.commit_grid.item(self.commit_grid.currentRow(), 0).text())
        add_comitments_unit(self.unit_id, self.cmt_type)
    
    
def add_comitments_unit(unit_id,cmt_type):
    if cmt_type == 15:
        form = classes_un.InputDateComits(title='Call Center', eternal=False)
        form.exec_()
        if form.ret[0]:
            c_end = form.ret[1]
            if gl.commit_types[cmt_type][6] == 1: # factura
                form = classes_un.InputInvoice()
                form.exec_()
                if form.ret[0]:
                    liblogos.add_unit_comitment(unit_id, cmt_type , c_end, form.ret[1], reset=True)

    elif cmt_type == 18: # users
        form = classes_un.AddInteger(-1, ['Utilizadores','Utilizadores Actuais','Utilizadores'])
        form.exec_()
        if form.ret[0]:
            t_add = form.ret[2]
            form = classes_un.InputInvoice()
            form.exec_()
            if form.ret[0]:
                liblogos.add_unit_comitment(unit_id,cmt_type, t_add, form.ret[1], reset=True) # adiciona tickects

    elif cmt_type == 12:
        form = classes_un.InputDateComits(title='Data do contracto', eternal=True)
        form.exec_()
        if form.ret[0]:
            liblogos.add_unit_comitment(unit_id, cmt_type, form.ret[1], invoice='', reset=True)

    elif cmt_type == 13:
        form = classes_un.InputDateComits(title='Data de Bloqueio', eternal=True)
        form.exec_()
        if form.ret[0]:
            liblogos.add_unit_comitment(unit_id, cmt_type, form.ret[1], invoice='', reset=True)
    
    elif cmt_type == 14:
        form = classes_un.InputDateComits(title='Validade da Licença', eternal=False)
        form.exec_()
        if form.ret[0]:
            liblogos.add_unit_comitment(unit_id, cmt_type, form.ret[1], invoice='', reset=True)
    # elif cmt_type == 21:
    #     b, ok = QInputDialog.getText(self, "Código IWS", "Código", QLineEdit.Normal)
    #     if ok and not b == '':
    #         pass
    #     else:
    #         pass
            



if __name__ == '__main__':
    pass
