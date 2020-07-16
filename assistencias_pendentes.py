#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, \
    QTableWidgetItem, QVBoxLayout, QTableWidget
from PyQt5.Qt import Qt
import parameters as pa
import data_sets
import qlib as qc


class PendingProcess(QDialog):
    def __init__(self, assistencias_pendentes, parent=None):
        super(PendingProcess, self).__init__(parent)
        self.resize(800, 600)
        self.setWindowTitle('Assistencias Pendentes')
        self.ret_dict = {}
        self.ret_dict['flag'] = 0
        pa.ass_montante = -2
        self.proc_montante = -1
        mainLayout = QVBoxLayout(self)
        label = QLabel('Existem as seguintes assistencias Pendentes.')
        
        mainLayout.addWidget(label)
        self.pendingGrid = QTableWidget(self)
        
        self.pendingGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.pendingGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.pendingGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.pendingGrid.verticalHeader().setDefaultSectionSize(20)
        self.pendingGrid.setAlternatingRowColors(True)
        self.pendingGrid.setStyleSheet("alternate-background-color: #e6ffee;")
        # self.pendingGrid.verticalHeader().setVisible(False)
        self.pendingGrid.resizeRowToContents(1)
        # self.pendingGrid.resiz()
        self.pendingGrid.itemDoubleClicked.connect(self.grid_click)
        
        mainLayout.addWidget(self.pendingGrid)
        self.make_grid()
        self.update_grid(assistencias_pendentes)
        self.linkaAssBtn = QPushButton('Continua')
        self.linkaAssBtn.clicked.connect(self.linka_click)
        self.novaAssBtn = QPushButton('Nova Assistencia')
        self.novaAssBtn.clicked.connect(self.nova_click)
        mainLayout.addLayout(qc.addHLayout([self.novaAssBtn]))
    
    def linka_click(self):
        self.grid_click()
    
    def nova_click(self):
        self.ret_dict['flag'] = 1 # nova
        self.close()
    
    def grid_click(self):
        self.proc_montante = int(self.pendingGrid.item(self.pendingGrid.currentRow(), 0).text())
        # carrega a assistencia a montante no dicionario e passa a utilizar esse dicionario
        # pa.assistencia_montanteDic = data_sets.assistencia_to_dict(self.assistencia_anterior)
        self.ret_dict.update(data_sets.assistencia_to_dict(self.proc_montante))
        self.ret_dict['proc_montante'] = self.proc_montante
        self.ret_dict['flag'] = 2 # de proc pendente
        self.close()
    
    def make_grid(self):
        self.pendingGrid.setColumnCount(4)
        self.pendingGrid.setHorizontalHeaderLabels(['ID', 'Data', 'Avaria', 'Técnico'])
        self.pendingGrid.setRowCount(0)
    
    def update_grid(self, dataSet):
        self.pendingGrid.setRowCount(len(dataSet))
        self.linha = 0
        for n in dataSet:
            col = 0
            item = QTableWidgetItem()
            self.pendingGrid.setItem(self.linha, col, item)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setText(str(n[0]))
            
            col += 1
            item = QTableWidgetItem()  # data
            self.pendingGrid.setItem(self.linha, col, item)
            item.setText(n[1].strftime('%d.%m.%Y'))
            
            col += 1
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.pendingGrid.setItem(self.linha, col, item)
            item.setText(n[2])
            
            col += 1
            item = QTableWidgetItem()
            self.pendingGrid.setItem(self.linha, col, item)
            item.setText(n[3])
            self.linha += 1
        self.pendingGrid.resizeColumnsToContents()
        self.pendingGrid.setColumnWidth(2, 420)
        self.pendingGrid.setColumnWidth(0, 70)
        for n in range(0,self.pendingGrid.rowCount()):
            self.pendingGrid.setRowHeight(n,90)
    
   

if __name__ == '__main__':
    pass
