#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton,QHBoxLayout, QButtonGroup
import libpg


class SetPendingStatus(QDialog):
    def __init__(self, parent = None):
        super(SetPendingStatus, self).__init__(parent)
        self.setWindowTitle('Estado do Pedido')
        self.toto = -1

        mainLayout = QVBoxLayout(self)
        mainLayout.addLayout(self.make_buttons(self.get_data()))
        # butoes
        self.closeBtn = QPushButton('Voltar')
        self.setSizes(self.closeBtn)
        self.closeBtn.clicked.connect(self.closeBtn_click)
        mainLayout.addWidget(self.closeBtn)

    def make_buttons(self,data):
        self.salesButtonsGroup = QButtonGroup()
        totoLayout = QHBoxLayout()
        col_size = 6
        colLayout = QVBoxLayout()
        col_cnt = 1
        for n in data:
            
            btn = QPushButton(n[1])
            self.setSizeWidth(btn, 300)
            self.setSizeHeight(btn,30)
            self.salesButtonsGroup.addButton(btn, n[0])
            if col_cnt < col_size :
                colLayout.addWidget(btn)
                col_cnt +=1
            elif col_cnt == col_size :
                colLayout.addWidget(btn)
                totoLayout.addLayout(colLayout)
                colLayout = QVBoxLayout()
                col_cnt = 1

        if col_cnt <= col_size:
            colLayout.addStretch()
            totoLayout.addLayout(colLayout)

        # self.connect(self.salesButtonsGroup, SIGNAL("buttonClicked(int)"), self.button_group_click)
        self.salesButtonsGroup.buttonClicked.connect(self.button_group_click)
        
        return totoLayout

    def button_group_click(self,btn):
        # # 0 tem o nome da acção e o 1 tem a accção
        self.toto = btn.text()
        self.close()

    def closeBtn_click(self):
        self.toto = -1
        self.close()

    def get_data(self):
        a = libpg.query_many('''select st_id, st_descricao, st_action
            from status  order by st_sort       ''',
            (True, ))
        return a

    #-------------------------------------------------
    def setSizes(self, object,value = 60):
        
        #object.setMaximumHeight (value)
        object.setMinimumHeight(value)
        #object.setMaximumWidth(value+20)
        object.setMinimumWidth(value)

    def setSizeWidth(self, object, value):
        object.setMaximumWidth(value)
        object.setMinimumWidth(value)
    
    def setSizeHeight(self, object, value):
        object.setMaximumHeight(value)
        object.setMinimumHeight(value)

    # def addHDumLayout(self, listobj1):
    #     dumLayout = QHBoxLayout()
    #     for n in listobj1:
    #         if (type(n)==str) or (type(n) == str):
    #             dumLayout.addWidget(QLabel(n))
    #         elif type(n) == bool:
    #             dumLayout.addStretch()
    #         else:
    #             dumLayout.addWidget(n)
    #     return dumLayout
    # def addVDumLayout(self, listobj1):
    #     dumLayout = QVBoxLayout()
    #     for n in listobj1:
    #         if (type(n)==str) or (type(n) == str):
    #             dumLayout.addWidget(QLabel(n))
    #         elif type(n) == bool:
    #             dumLayout.addStretch()
    #         else:
    #             dumLayout.addWidget(n)
    #     return dumLayout
    #
    # def parseField(self, field_name):
    #     # v2
    #     dum = self.item_data[field_name]
    #     if type(dum) == int:
    #         return str(dum)
    #     elif dum == None:
    #         return ''
    #     else:
    #         return dum

if __name__ == '__main__':
    pass