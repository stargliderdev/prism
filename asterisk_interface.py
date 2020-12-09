#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QSpinBox, QTableWidgetItem, QHBoxLayout, \
    QTableWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import time
import datetime
import MySQLdb
import parameters as gl
import qlib


class AsteriskInterface(QDialog):
    def __init__(self, parent=None):
        super(AsteriskInterface, self).__init__(parent)
        self.resize(800, 600)
        self.setWindowTitle('Ultimas Chamadas')
        self.toto = {} # {'call_number': '', 'call_unit': '', 'call_who': '', 'call_cdr': ''}
        gl.ass_montante = -2
        gl.asterisk_stack_call = {}
        mainLayout = QVBoxLayout(self)
        
        self.call_count = QSpinBox()
        self.call_count.setMaximumWidth(80)
        self.call_count.setValue(101)
        self.call_count.setMaximum(30000)
        self.call_count.setMinimum(1)
        self.call_count.setSingleStep(10)
        
        self.update_Btn = QPushButton('Actualiza')
        self.update_Btn.setMaximumWidth(120)
        self.update_Btn.clicked.connect(self.refresh_click)
        mainLayout.addLayout(qlib.addHLayout(['Ultimas chamadas', self.call_count, self.update_Btn], 120))
        self.grid = QTableWidget(self)
        
        self.grid.setSelectionBehavior(QTableWidget.SelectRows)
        self.grid.setSelectionMode(QTableWidget.SingleSelection)
        self.grid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.grid.verticalHeader().setDefaultSectionSize(20)
        # self.grid.setAlternatingRowColors (True)
        self.grid.verticalHeader().setVisible(False)
        self.grid.setStyleSheet("alternate-background-color: #e6faff;")
        mainLayout.addWidget(self.grid)
        
        # butoes
        self.exit = QPushButton('Sair')
        self.setSizes(self.exit)
        self.exit.clicked.connect(self.exit_click)
        
        self.okBtn = QPushButton('Valida')
        self.setSizes(self.okBtn)
        self.okBtn.clicked.connect(self.validate_choice)
        
        mainLayout.addLayout(qlib.addHLayout([self.okBtn, self.exit]))
        
        self.make_grid()
        self.update_grid(get_last_calls())
    
    def refresh_click(self):
        self.update_grid(get_last_calls(self.call_count.value()))
    
    def exit_click(self):
        self.close()
    
    def validate_choice(self):
        time_total = datetime.timedelta(seconds=0)
        cdr_dum = ''
        for linha in range(0, self.grid.rowCount()):
            if self.grid.item(linha, 0) is not None:  # == None:
                pass
            else:
                
                if self.grid.cellWidget(linha, 0).layout().itemAt(1).widget().isChecked():
                    self.toto['call_date'] = datetime.datetime.strptime(str(self.grid.item(linha, 1).text()), '%d-%m-%Y %H:%M:%S')
                    d1 = datetime.datetime.strptime(str(self.grid.item(linha, 4).text()), "%M:%S")
                    time_total = time_total + datetime.timedelta(minutes=d1.minute + 1, seconds=d1.second)
                    who_call = self.grid.item(linha, 2).text().split(':')
                    self.toto['call_number'] = str(self.grid.item(linha, 3).text())
                    cdr = self.grid.item(linha, 1).text() + ' ' + self.grid.item(linha, 2).text() + ' ' + \
                          self.grid.item(linha, 3).text() + ' ' + self.grid.item(linha, 4).text() + ' ' + \
                          self.grid.item(linha, 5).text()
                    cdr_dum +=cdr + '\n'
        if cdr_dum != '':
            self.toto['call_cdr'] = cdr_dum
        else:
            self.toto = {}
        if self.toto == {}:
            pass
        else:
            if len(who_call) > 1:
                self.toto['call_unit'] = who_call[0]
                self.toto['call_who'] = who_call[1].strip()
            
            self.toto['call_time'] = datetime.datetime.strptime(str(time_total), "%H:%M:%S")
        self.close()
    
    def make_grid(self):
        self.grid.setColumnCount(7)
        self.grid.setHorizontalHeaderLabels(['Marca', 'Data', 'Origem', 'Numero', 'Tempo', 'Resultado', 'Destino'])
        self.grid.setRowCount(0)
        self.grid.setColumnWidth(5, 0)
    
    def update_grid(self, dataSet):
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        rows = len(dataSet)
        self.grid.setRowCount(rows)
        linha = 0
        stack = dataSet[0][2]
        for n in dataSet:
            # if stack != n[2]:
            #     rows +=1
            #     self.grid.setRowCount(rows)
            #     stack = n[2]
            #     item = QTableWidgetItem()
            #     item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            #     #self.grid.setCellWidget(linha, 0, QCheckBox())
            #     self.grid.setItem(linha, 0, item)
            #     linha +=1
            
            self.grid.setCellWidget(linha, 0, qlib.checkBoxGrid())
            
            item = QTableWidgetItem()
            self.grid.setItem(linha, 1, item)
            item.setText(n[0].strftime("%d-%m-%Y %H:%M:%S"))
            if n[6] != '':
                item.setFont(font)
            
            item = QTableWidgetItem()
            self.grid.setItem(linha, 2, item)
            if n[1].find(':') >= 0:
                item.setText(clean(n[1]))
            else:
                item.setText(n[1])
            if n[6] != '':
                item.setFont(font)
            
            item = QTableWidgetItem()
            self.grid.setItem(linha, 3, item)
            item.setText(n[2])
            if n[6] != '':
                item.setFont(font)
            
            item = QTableWidgetItem()
            self.grid.setItem(linha, 4, item)
            item.setText(time.strftime('%M:%S', time.gmtime(n[3])))
            if n[6] != '':
                item.setFont(font)
            item = QTableWidgetItem()
            self.grid.setItem(linha, 5, item)
            item.setText(n[5])
            if n[6] != '':
                item.setFont(font)
            
            item = QTableWidgetItem()
            self.grid.setItem(linha, 6, item)
            item.setText(n[6])
            if n[6] != '':
                item.setFont(font)
            
            linha += 1
        self.grid.resizeColumnsToContents()
        self.grid.setColumnWidth(2, 320)
        self.grid.setColumnWidth(5, 0)
    
    def setSizes(self, object, value=60):
        # object.setMaximumHeight (value)
        object.setMinimumHeight(value)
        # object.setMaximumWidth(value+20)
        object.setMinimumWidth(value)


def get_last_calls(limit=50, group=False, ):
    db = MySQLdb.connect(host="192.168.0.204",  # your host, usually localhost
                         user="root",  # your username
                         passwd="BarcaVelha1999",  # your password
                         db="asteriskcdrdb")  # name of the data base
    
    cur = db.cursor()
    sql = "SELECT calldate,clid,src,duration,billsec,disposition,dstchannel FROM cdr order by calldate desc limit " + str(
        limit)
    cur.execute(sql)
    toto = cur.fetchall()
    cur.close()
    asterisk_list = []
    for n in toto:
        if n[4] > 15:
            try:  # remove a duplicação de linhas
                a = int(n[1])
            except ValueError:
                asterisk_list.append((n[0], n[1].replace('"',''), n[2], n[3], n[4], n[5], clean_dst(n[6])))
    return asterisk_list


def clean(text):
    toto = text.split('<')
    return toto[0].replace('"', '')


def clean_dst(text):
    toto = ''
    if text.find('SIP') > -1:
        return ''
    else:
        toto = text.split('@')
        toto[0] = toto[0].replace('Local/', '')
        return toto[0]


if __name__ == '__main__':
    pass
    # for n in get_last_calls():
    #     # print(n[0],n[1],n[2],n[3],n[4],n[5],clean_dst(n[6]))
    #     print(n[0].strftime("%d-%m-%Y %H:%M:%S").ljust(20), '|', "{:<54}".format(n[1]), '|', n[2].ljust(10), '|',
    #           str(n[3]).ljust(10),
    #           str(n[4]).ljust(20), str(n[5]).ljust(20),
    #           str(n[6]).ljust(20))
