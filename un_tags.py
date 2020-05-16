#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QTableWidget, QInputDialog

import ex_grid
import libpg
import qlib as qc


class UnitTagsBrowser(QDialog):
    def __init__(self, mode = 1, parent = None):
        super(UnitTagsBrowser,  self).__init__(parent)
        # self.setWindowFlags(Qt.FramelessWindowHint) #|Qt.WindowStaysOnTopHint) #|Qt.WindowTitleHint)
        self.resize(620, 440)
        self.setWindowTitle('Etiquetas de Unidades')
        masterLayout = QVBoxLayout(self)
        # masterLayout.setContentsMargins (1,1,1,1)
        # masterLayout.setSpacing(0)
        self.tag_list = ''
        deselect_tags_Btn=QPushButton('Des-seleciona')
        # self.connect(deselect_tags_Btn, SIGNAL("clicked()"), self.deselect_click )

        clean_tranf_Btn=QPushButton('Limpa Transferidas')
        # self.connect(clean_tranf_Btn, SIGNAL("clicked()"), self.clean_transfer)
        clean_tranf_Btn.clicked.connect(self.clean_transfer)
        
        add_tag_Btn=QPushButton('Adiciona')
        add_tag_Btn.clicked.connect(self.add_new_tag)
        
        if mode == 1:
            masterLayout.addLayout(qc.addHLayout([deselect_tags_Btn,clean_tranf_Btn,add_tag_Btn,True]))
        elif mode == 2:
            masterLayout.addLayout(qc.addHLayout([deselect_tags_Btn,clean_tranf_Btn,True]))
        self.searchEdit = QLineEdit()
        self.toto = ()
        self.searchEdit.textChanged.connect(self.tag_search_changed)
        # 
        masterLayout.addWidget(self.searchEdit)
        self.grid = QTableWidget()
        self.grid.setSelectionBehavior(QTableWidget.SelectRows)
        self.grid.setSelectionMode(QTableWidget.MultiSelection)
        self.grid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.grid.verticalHeader().setDefaultSectionSize(20)
        self.grid.verticalHeader().setVisible(False)
        self.grid.resizeColumnsToContents()
        self.grid.itemDoubleClicked.connect(self.transfer_click)
        # transferBtn = QPushButton('Transfere')
        # transferBtn.clicked.connect(self.transfer_click)
        self.current_tags = QTextEdit()
        masterLayout.addLayout(qc.addHLayout([self.grid,self.current_tags]))
        exit_btn = QPushButton('Sair')
        exit_btn.clicked.connect(self.exit_click)
        valid_btn = QPushButton('Valida')
        valid_btn.clicked.connect(self.valid_click)
        # add_btn = QPushButton('Adiciona')
        # valid_btn.clicked.connect(self.add_tags_click)
        
        # if mode == 1:
        #     masterLayout.addLayout(qc.addHLayout([valid_btn,exit_btn]))
        # if mode == 2:
        #     add_btn.setText('Valida')
        masterLayout.addLayout(qc.addHLayout([valid_btn,exit_btn]))
        self.tag_refresh()

    def deselect_click(self):
        self.grid.clearSelection()

    def clean_transfer(self):
        self.current_tags.clear()

    def add_new_tag(self):
        b, ok = QInputDialog.getText(self, "Nova Etiqueta", "Nova Etiqueta", QLineEdit.Normal)
        if ok and not b == '':
            if self.current_tags.toPlainText() == '':
                self.current_tags.setText(b)
            else:
             self.current_tags.setText(self.current_tags.toPlainText() + ',' + b)
        else:
            print('do nothing')

    def transfer_click(self):
        self.tag_list = ''
        for n in self.grid.selectedIndexes():
            # self.tag_id.append(int(self.grid.item(n.row(),0).text()))
            self.tag_list += str(self.grid.item(n.row(),1).text()) + ','
        if self.current_tags.toPlainText() == '':
            self.current_tags.setText(self.tag_list[0:-1])
        else:
            self.current_tags.setText(self.current_tags.toPlainText() +  ',' + self.tag_list[0:-1])
        self.grid.clearSelection()

    def valid_click(self):
        # self.tag_id = 0
        self.tag_list = (0, self.current_tags.toPlainText())
        self.close()

    def add_click(self):
        # self.tag_id = 1
        self.tag_list = (1, self.current_tags.toPlainText())
        self.close()

    def tag_refresh(self):
        self.c_grid = 10
        sql = '''select tau_id, tau_name from tags_unit order by tau_name'''
        dataset = libpg.query_many(sql, True)
        ex_grid.ex_grid_update (self.grid, {0:['ID','i'],1:['Nome', 's']}, dataset, hidden=0)
        self.grid.horizontalHeader().setVisible(False)
        self.grid.setColumnWidth(0, 80)
        self.grid.setColumnWidth(1, 200)

    def tag_search_changed(self, text):
        if  len(text)>3:
            search = '\'%%' + text + '%%\''
            # print 'search ',text
            sql = '''select tau_id, tau_name from tags_unit where tau_name like ''' + search + ''' order by tau_name'''
            dataset = libpg.query_many(sql, True)
            ex_grid.ex_grid_update (self.grid, {0:['ID','i'],1:['Nome', 's']}, dataset, hidden=0)
            self.grid.horizontalHeader().setVisible(False)
            self.grid.setColumnWidth(0, 80)
            self.grid.setColumnWidth(1, 200)

    def exit_click(self):
        self.tag_list = (2,'')
        self.close()

# class EditRecordTags(QDialog):
#     def __init__(self, tags_data, parent = None):
#         super(EditRecordTags,  self).__init__(parent)
#         # self.setWindowFlags(Qt.FramelessWindowHint) #|Qt.WindowStaysOnTopHint) #|Qt.WindowTitleHint)
#         self.resize(200, 350)
#         self.setWindowTitle('Edita Etiquetas do Registo')
#         self.tags_data = tags_data
#         masterLayout = QVBoxLayout(self)
#         masterLayout.setContentsMargins(1,1,1,1)
#         masterLayout.setSpacing(0)
#         self.searchEdit = QLineEdit()
#         self.toto = ()
#         self.connect(self.searchEdit,SIGNAL("textChanged(QString)"),self.tag_search_changed)
#         masterLayout.addWidget(self.searchEdit)
#         self.grid = QTableWidget()
#         # self.grid.setSelectionBehavior(QTableWidget.SelectRows)
#         # self.grid.setSelectionMode(QTableWidget.MultiSelection)
#         self.grid.setSelectionBehavior(QTableWidget.SelectRows)
#         self.grid.setSelectionMode(QTableWidget.SingleSelection)
#         self.grid.setEditTriggers(QTableWidget.AllEditTriggers)
#         # self.grid.setEditTriggers(QTableWidget.NoEditTriggers)
#         self.grid.verticalHeader().setDefaultSectionSize(20)
#         # self.grid.setAlternatingRowColors (True)
#         self.grid.verticalHeader().setVisible(False)
#         self.grid.resizeColumnsToContents()
#         masterLayout.addWidget(self.grid)
#         exit_btn=QPushButton('Sair')
#         self.connect(exit_btn, SIGNAL("clicked()"), self.exit_click)
#         valid_btn=QPushButton('Valida')
#         self.connect(valid_btn, SIGNAL("clicked()"), self.valid_click)
#         masterLayout.addLayout(qc.addHLayout([valid_btn,exit_btn]))
#
#         self.tag_refresh()
#
#     def valid_click(self):
#         self.tag_list=''
#         # self.tag_id=[]
#         for linha in range(0, self.grid.rowCount()):
#             # if self.grid_1.cellWidget(linha, 1) is not None:
#                 # if self.grid_1.cellWidget(linha, 1).layout().itemAt(1).widget().isChecked():
#                 # if self.grid_1.cellWidget(linha, 1).isChecked() :
#                     # print int(self.grid.item(linha, 0).text())
#                     # tags_1.append(unicode(self.grid_1.item(linha, 2).text()))
#             self.tag_list += str(self.grid.item(linha,1).text()) +','
#         # print self.grid.selectedIndexes().selectedRows()
#         self.tag_list = self.tag_list[0:-1]
#         self.close()
#
#     def tag_refresh(self):
#         self.c_grid = 10
#         ex_grid.ex_grid_update (self.grid, {0:['ID','i'],1:['Nome', 's']}, self.tags_data, hidden=0)
#         self.grid.horizontalHeader().setVisible(False)
#         self.grid.setColumnWidth(0, 80)
#         self.grid.setColumnWidth(1, 200)
#
#     def tag_search_changed(self, text):
#         if len(text)>3:
#             search = '\'%%' + text + '%%\''
#             # print 'search ',text
#             sql = '''select tau_id, tau_name from tags_unit where tau_name like ''' + search + ''' order by tau_name'''
#             dataset = libpg.query_many(sql, True)
#             ex_grid.ex_grid_update (self.grid, {0:['ID','i'],1:['Nome', 's']}, dataset, hidden=0)
#             self.grid.horizontalHeader().setVisible(False)
#             self.grid.setColumnWidth(0, 80)
#             self.grid.setColumnWidth(1, 200)
#
#     def exit_click(self):
#         self.tag_list = ''
#         self.close()



if __name__ == '__main__':
    pass

