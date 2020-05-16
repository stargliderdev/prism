#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QLabel,QVBoxLayout,QPushButton, QSpinBox, QTableWidgetItem, QHBoxLayout,QTableWidget
from PyQt5.QtCore import Qt
import time
import datetime
import MySQLdb
import parameters as pa
import qlib


class AsteriskInterface(QDialog):
    def __init__(self, parent = None):
        super(AsteriskInterface,  self).__init__(parent)
        self.resize(800, 600)
        self.setWindowTitle('Ultimas Chamadas') 
        self.toto = {'call_number': '','call_unit':'','call_who':'','call_cdr':''}
        pa.ass_montante = -2
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
        mainLayout.addLayout(self.addHDumLayout(['Ultimas chamadas',self.call_count, self.update_Btn],120))
        self.grid = QTableWidget(self)

        self.grid.setSelectionBehavior(QTableWidget.SelectRows)
        self.grid.setSelectionMode(QTableWidget.SingleSelection)
        self.grid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.grid.verticalHeader().setDefaultSectionSize(20)
        self.grid.setAlternatingRowColors (True)
        self.grid.verticalHeader().setVisible(False)
        mainLayout.addWidget(self.grid)

        # butoes
        self.exit = QPushButton('Cancelar') 
        self.setSizes(self.exit)
        self.exit.clicked.connect(self.exit_click)
        
        self.okBtn = QPushButton('Aceita')
        self.setSizes(self.okBtn) 
        self.okBtn.clicked.connect(self.nova_click)
        
        mainLayout.addLayout(self.addHDumLayout([self.okBtn,self.exit]))

        self.make_grid()
        self.update_grid(get_last_calls())

    def refresh_click(self):
        self.update_grid(get_last_calls(self.call_count.value()))

    def exit_click(self):

        self.close()

    def nova_click(self):
        time_total = datetime.timedelta(seconds =0)
        for linha in range(0, self.grid.rowCount()):
            if self.grid.item(linha, 0) is not None: #== None:
                pass    
            else:
                if self.grid.cellWidget(linha, 0).layout().itemAt(1).widget().isChecked(): #  .isChecked(): # foi escolhido
                    self.toto['call_date'] = datetime.datetime.strptime(str(self.grid.item(linha,1).text()), '%d-%m-%Y %H:%M:%S')
                    d1 = datetime.datetime.strptime(str(self.grid.item(linha, 4).text()), "%M:%S")
                    time_total = time_total + datetime.timedelta(minutes=d1.minute + 1,seconds=d1.second)
                    who_call = str(self.grid.item(linha,2).text()).split(':')
                    self.toto['call_number'] = str(self.grid.item(linha,3).text())
                    cdr = self.grid.item(linha, 1).text() + ' ' + self.grid.item(linha, 2).text() + ' ' + \
                            self.grid.item(linha, 3).text() + ' ' + self.grid.item(linha, 4).text() + ' ' +\
                            self.grid.item(linha, 5).text()
                    self.toto['call_cdr'] += cdr + '\n'
        
        if self.toto['call_number'] == '':
            pass
        else:
            if len(who_call) >1:
                self.toto['call_unit'] = who_call[0]
                self.toto['call_who'] = who_call[1]
                
            self.toto['call_time'] = time_total
        self.close()


    def make_grid(self):
        self.grid.setColumnCount(7)
        self.grid.setHorizontalHeaderLabels(['Marca','Data','Origem','Numero','Tempo','Resultado','Destino'])
        self.grid.setRowCount(0)

    def update_grid(self, dataSet):    
            rows = len(dataSet)
            self.grid.setRowCount(rows)
            linha = 0
            stack = dataSet[0][2]
            for n in dataSet:
                    if stack != n[2]:
                        rows +=1
                        self.grid.setRowCount(rows)
                        stack = n[2]
                        item = QTableWidgetItem()
                        item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                        #self.grid.setCellWidget(linha, 0, QCheckBox())
                        self.grid.setItem(linha, 0, item)
                        linha +=1
                
                    # item = QTableWidgetItem()
                    # item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                    # self.grid.setCellWidget(linha, 0, QCheckBox())
                    self.grid.setCellWidget(linha, 0, qlib.checkBoxGrid())
                    # self.grid.setItem(linha, 0, item)

                    item = QTableWidgetItem()
                    self.grid.setItem(linha, 1,item )
                    item.setText(n[0].strftime("%d-%m-%Y %H:%M:%S"))           

                    item = QTableWidgetItem() # data
                    self.grid.setItem(linha, 2,item )
                    if n[1].find(':') >= 0 :
                        # item.setTextColor(QColor(0,0,255))
                        item.setText(clean(n[1])) 
                    else:
                        item.setText(n[1])

                    item = QTableWidgetItem()
                    self.grid.setItem(linha, 3,item )
                    item.setText(n[2])

                    item = QTableWidgetItem()
                    self.grid.setItem(linha, 4,item )
                    item.setText(time.strftime('%M:%S', time.gmtime(n[3])))

                    item = QTableWidgetItem()
                    # if n[5] == 'ANSWERED':
                    #     item.setTextColor(QColor(0,150,0))
                    # if n[5] == 'NO ANSWER':
                    #     item.setTextColor(QColor(255,150,0))
                    self.grid.setItem(linha, 5,item )
                    item.setText(n[5])

                    item = QTableWidgetItem()
                    self.grid.setItem(linha, 6,item )
                    item.setText(clean_dst(n[6]))

                    linha +=1
            self.grid.resizeColumnsToContents()
            self.grid.setColumnWidth(2, 180)

    def qc(self,qstring):
        return qstring

    def setSizes(self, object,value = 60):
        #object.setMaximumHeight (value)
        object.setMinimumHeight(value)
        #object.setMaximumWidth(value+20)
        object.setMinimumWidth(value)

    def setSizeWidth(self, object, value):
        object.setMaximumWidth(value)
        object.setMinimumWidth(value)


    def addHDumLayout(self, listobj1, lb = 90, align = Qt.AlignVCenter|Qt.AlignRight):
        """ v 2.0 SET2012"""  
        dumLayout = QHBoxLayout()
        for n in listobj1:        
            if (type(n)==str) or (type(n) == str):
                toto = QLabel(n)
                toto.setMinimumWidth(lb)
                toto.setMaximumWidth(lb)
                toto.setAlignment(align)
                dumLayout.addWidget(toto)
            elif type(n) == bool:
                dumLayout.addStretch()

            else:

                dumLayout.addWidget(n)
        return dumLayout
        
    def addVDumLayout(self, listobj1, lb = 120, align = Qt.AlignVCenter|Qt.AlignRight):
        """ v 2.0 SET2012"""  
        dumLayout = QVBoxLayout()
        for n in listobj1:        
            if (type(n)==str) or (type(n) == str):
                toto = QLabel(n)
                toto.setMinimumWidth(lb)
                toto.setMaximumWidth(lb)
                toto.setAlignment(align)
                dumLayout.addWidget(toto)
            elif type(n) == bool:
                dumLayout.addStretch()
            else:

                dumLayout.addWidget(n)
        return dumLayout

    def parseField(self, field_name):
        # v2
        dum = self.item_data[field_name]
        if type(dum) == int:
            return str(dum)
        elif dum == None:
            return ''
        else:
            return dum

def get_last_calls(limit=100, group = False,):
    db = MySQLdb.connect(host="192.168.0.204", # your host, usually localhost
                         user="root", # your username
                          passwd="BarcaVelha1999", # your password
                          db="asteriskcdrdb") # name of the data base

    cur = db.cursor() 
    sql = "SELECT calldate,clid,src,duration,billsec,disposition,dstchannel FROM cdr order by calldate desc limit " + str(limit)
    cur.execute(sql)
    toto = cur.fetchall()

    return toto

def clean(text):
    toto= text.split('<')
    return toto[0].replace('"','')
def clean_dst(text):
    toto = text.split('@')
    toto[0] = toto[0].replace('Local/','')
    return toto[0]

if __name__ == '__main__':
    pass
