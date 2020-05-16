#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QPushButton, QApplication, QLineEdit, QTextEdit, \
    QInputDialog, QToolButton, QHBoxLayout
from PyQt5.QtGui import QIcon
import sys
import libpg
import ex_grid
import qlib as qc


class ProcessTagsBrowser(QDialog):
    def __init__(self, mode=2, parent=None):
        super(ProcessTagsBrowser, self).__init__(parent)
        self.resize(720, 420)
        self.setWindowTitle('Tags do pedido')
        masterLayout = QVBoxLayout(self)
        subLayout = QHBoxLayout()
        self.tag_list = (2, '')
        cleanTranfTBtn = QToolButton()
        cleanTranfTBtn.setIcon(QIcon('.//img//broom.png'))
        cleanTranfTBtn.clicked.connect(self.clean_transfer)
        
        add_tag_Btn = QPushButton('Adiciona')
        add_tag_Btn.clicked.connect(self.add_new_tag)
        
        # if mode == 1:
        #     masterLayout.addLayout(qc.addHLayout([clean_tranf_Btn, add_tag_Btn, True]))
        # elif mode == 2:
        # masterLayout.addLayout(qc.addHLayout([clean_tranf_Btn, True]))
        self.searchEdit = QLineEdit()
        self.newTagEdit = QLineEdit()
        addNewTBtn = QToolButton()
        addNewTBtn.setIcon(QIcon('.//img//add_tag.png'))
        addNewTBtn.clicked.connect(self.add_tag_click)
        self.currentTagsTEdt = QTextEdit()
        
        self.toto = ()
        self.searchEdit.textChanged.connect(self.tag_search_changed)
        
        self.tagsGrid = QTableWidget()
        self.tagsGrid.setSelectionBehavior(QTableWidget.SelectRows)
        # self.grid.setSelectionMode(QTableWidget.MultiSelection)
        self.tagsGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.tagsGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tagsGrid.verticalHeader().setDefaultSectionSize(20)
        self.tagsGrid.verticalHeader().setVisible(False)
        self.tagsGrid.resizeColumnsToContents()
        self.tagsGrid.itemDoubleClicked.connect(self.transfer_click)
        self.tagsGrid.setAlternatingRowColors(True)
        self.tagsGrid.setStyleSheet("alternate-background-color: #f9ecf2;")
        exit_btn = QPushButton('Sair')
        exit_btn.clicked.connect(self.exit_click)
        valid_btn = QPushButton('Valida')
        valid_btn.clicked.connect(self.valid_click)
        
        # add_btn = QPushButton('Adiciona')
        # add_btn.clicked.connect(self.add_tags_click)
        
        subLayout.addLayout(qc.addVLayout([self.searchEdit, self.tagsGrid]))
        dum = QVBoxLayout()
        dum.addLayout(qc.addHLayout([self.newTagEdit, addNewTBtn, cleanTranfTBtn]))
        dum.addWidget(self.currentTagsTEdt)
        subLayout.addLayout(dum)
        masterLayout.addLayout(subLayout)
        self.tag_refresh()
        self.searchEdit.setFocus()
        masterLayout.addLayout(qc.addHLayout([valid_btn, exit_btn]))
        
    def deselect_click(self):
        self.tagsGrid.clearSelection()
    
    
    def clean_transfer(self):
        self.currentTagsTEdt.clear()
    
    def add_tag_click(self):
        self.currentTagsTEdt.setText(self.currentTagsTEdt.toPlainText() + ',' + self.newTagEdit.text().lower())
        self.newTagEdit.clear()
    
    def add_new_tag(self):
        b, ok = QInputDialog.getText(self, "Nova Etiqueta", "Nova Etiqueta", QLineEdit.Normal)
        if ok and b is None:
            if self.currentTagsTEdt.toPlainText() is None:
                self.currentTagsTEdt.setText(b)
            else:
                self.currentTagsTEdt.setText(self.currentTagsTEdt.toPlainText() + ',' + b)
        else:
            print('do nothing')
    
    def transfer_click(self):
        self.tag_list = ''
        for n in self.tagsGrid.selectedIndexes():
            self.tag_list += str(self.tagsGrid.item(n.row(), 0).text()) + ','
        if self.currentTagsTEdt.toPlainText() is None:
            self.currentTagsTEdt.setText(self.tag_list[0:-1])
        else:
            self.currentTagsTEdt.setText(self.currentTagsTEdt.toPlainText() + ',' + self.tag_list[0:-1])
        # self.grid.clearSelection()
        self.searchEdit.clear()
        self.searchEdit.setFocus()
        
    def valid_click(self):
        # self.tag_id = 0
        self.tag_list = (0, self.currentTagsTEdt.toPlainText()[1:])
        self.close()
    
    def tag_refresh(self):
        self.c_grid = 10
        sql = '''select tag from tags order by tag'''
        # sql = '''select tag from tags where tag_level=0 order by tag'''
        dataset = libpg.query_many(sql, True)
        ex_grid.ex_grid_update(self.tagsGrid, {0: ['Nome', 's']}, dataset)
        self.tagsGrid.horizontalHeader().setVisible(False)
        self.tagsGrid.setColumnWidth(0, 200)
    
    def tag_search_changed(self, text):
        search = '\'' + self.searchEdit.text().lower() + '%%\''
        # print 'search ',text
        sql = '''select tag from tags where lower(tag) like ''' + search + ''' order by tag'''
        dataset = libpg.query_many(sql, True)
        ex_grid.ex_grid_update(self.tagsGrid, {0: ['Nome', 's']}, dataset)
        self.tagsGrid.horizontalHeader().setVisible(False)
        self.tagsGrid.setColumnWidth(0, 200)
    
    def exit_click(self):
        self.tag_list = (2, '')
        self.close()

def main():
    app = QApplication(sys.argv)
    form = ProcessTagsBrowser()
    form.show()
    app.exec_()
    print(form.tag_list)

if __name__ == '__main__':
    main()
