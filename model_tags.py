#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QTableWidget, QInputDialog
import ex_grid
import libpg
import qlib as qc


class ModelTagsBrowser(QDialog):
    def __init__(self, mode=1, parent=None):
        super(ModelTagsBrowser, self).__init__(parent)
        self.resize(620, 440)
        self.setWindowTitle('Etiquetas dos Modelo')
        masterLayout = QVBoxLayout(self)
        self.tag_list = ''
        deselect_tags_Btn = QPushButton('Des-seleciona')
        deselect_tags_Btn.clicked.connect(self.deselect_click)
        
        clean_tranf_Btn = QPushButton('Limpa Transferidas')
        # self.connect(clean_tranf_Btn, SIGNAL("clicked()"), self.clean_transfer)
        clean_tranf_Btn.clicked.connect(self.clean_transfer)
        
        add_tag_Btn = QPushButton('Adiciona')
        # self.connect(add_tag_Btn, SIGNAL("clicked()"), self.add_new_tag)
        add_tag_Btn.clicked.connect(self.add_new_tag)
        
        if mode == 1:
            masterLayout.addLayout(qc.addHLayout([deselect_tags_Btn, clean_tranf_Btn, add_tag_Btn, True]))
        elif mode == 2:
            masterLayout.addLayout(qc.addHLayout([deselect_tags_Btn, clean_tranf_Btn, True]))
        self.searchEdit = QLineEdit()
        self.toto = ()
        # self.connect(self.searchEdit,SIGNAL("textChanged(QString)"),self.tag_search_changed)
        self.searchEdit.textChanged.connect(self.tag_search_changed)
        
        masterLayout.addWidget(self.searchEdit)
        self.grid = QTableWidget()
        self.grid.setSelectionBehavior(QTableWidget.SelectRows)
        self.grid.setSelectionMode(QTableWidget.MultiSelection)
        
        self.grid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.grid.verticalHeader().setDefaultSectionSize(20)
        # self.grid.setAlternatingRowColors (True)
        self.grid.verticalHeader().setVisible(False)
        self.grid.resizeColumnsToContents()
        self.grid.doubleClicked.connect(self.transfer_click)
        
        
        # transferBtn = QPushButton('Transfere')
        # self.connect(transferBtn, SIGNAL("clicked()"), self.transfer_click)
        # transferBtn.clicked.connect(self.transfer_click)
        
        self.current_tags = QTextEdit()
        
        masterLayout.addLayout(qc.addHLayout([self.grid, self.current_tags]))
        exit_btn = QPushButton('Sair')
        # self.connect(exit_btn, SIGNAL("clicked()"), self.exit_click)
        exit_btn.clicked.connect(self.exit_click)
        
        validBtn = QPushButton('Valida')
        # self.connect(valid_btn, SIGNAL("clicked()"), self.valid_click)
        validBtn.clicked.connect(self.valid_click)
        
        # addTagsBtn = QPushButton('Adiciona')
        # # self.connect(add_btn, SIGNAL("clicked()"), self.add_tags_click)
        # add_tag_Btn.clicked.connect(self.add_tags_click)
        
        # if mode == 1:
        masterLayout.addLayout(qc.addHLayout([validBtn, exit_btn]))
        # if mode == 2:
        #     addTagsBtn.setText('Valida')
        # masterLayout.addLayout(qc.addHLayout([addTagsBtn, exit_btn]))
        self.tag_refresh()

    def deselect_click(self):
        self.grid.clearSelection()
    
    def clean_transfer(self):
        self.current_tags.clear()
    
    def add_new_tag(self):
        b, ok = QInputDialog.getText(self, self.tr("Nova Etiqueta"), self.tr("Nova Etiqueta"), QLineEdit.Normal)
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
            self.tag_list += str(self.grid.item(n.row(), 1).text()) + ','
        if self.current_tags.toPlainText() == '':
            self.current_tags.setText(self.tag_list[0:-1])
        else:
            self.current_tags.setText(self.current_tags.toPlainText() + ',' + self.tag_list[0:-1])
        self.grid.clearSelection()
    
    def valid_click(self):
        # self.tag_id = 0
        self.tag_list = (0, self.current_tags.toPlainText())
        self.close()
    
    def add_tags_click(self):
        # self.tag_id = 1
        self.tag_list = (1, self.current_tags.toPlainText())
        self.close()
    
    def tag_refresh(self):
        self.c_grid = 10
        sql = '''select tam_id, tam_name from tags_model order by tam_name'''
        dataset = libpg.query_many(sql, True)
        ex_grid.ex_grid_update(self.grid, {0: ['ID', 'i'], 1: ['Nome', 's']}, dataset, hidden=0)
        self.grid.horizontalHeader().setVisible(False)
        self.grid.setColumnWidth(0, 80)
        self.grid.setColumnWidth(1, 200)
    
    def tag_search_changed(self, text):
        if len(text) > 3:
            search = '\'%%' + text + '%%\''
            # print 'search ',text
            sql = '''select tam_id, tam_name from tags_model where tam_name like ''' + search + ''' order by tam_name'''
            dataset = libpg.query_many(sql, True)
            ex_grid.ex_grid_update(self.grid, {0: ['ID', 'i'], 1: ['Nome', 's']}, dataset, hidden=0)
            self.grid.horizontalHeader().setVisible(False)
            self.grid.setColumnWidth(0, 80)
            self.grid.setColumnWidth(1, 200)
    
    def exit_click(self):
        self.tag_list = (2, '')
        self.close()
