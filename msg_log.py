#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout, QTableWidget, QHBoxLayout, QPushButton

import ex_grid
import liblogos
import libpg
import qlib as qc
import report_display


class MsgLogBrowser(QDialog):
    def __init__(self, unit_id=0, msg_type=0, parent=None):
        super(MsgLogBrowser, self).__init__(parent)
        self.resize(1024, 768)
        self.setWindowTitle('Registo de Mensagens')
        self.filter = []
        masterLayout = QVBoxLayout(self)
        filterLayout = QHBoxLayout()
        refrehBtn = QPushButton('Actualiza')
        exitBtn = QPushButton('Sair')
        exitBtn.clicked.connect(self.exit_click)
        
        masterLayout.addLayout(qc.addHLayout([True, exitBtn]))
        # self.unitNmaeEdt = QLineEdit()
        # self.destinationEdt = QLineEdit()
        # self.msgTypeCbx = QComboBox()
        # self.msgTypeCbx.addItems(['Todos','SMS', 'mail'])
        # filterLayout.addLayout( qc.addHLayout(['Unidade', self.unitNmaeEdt, 'Destion', self.destinationEdt, 'Tipo', self.msgTypeCbx]))
        # masterLayout.addLayout(filterLayout)
        self.gridMsgLog = QTableWidget()
        # self.gridMsgLog.itemDoubleClicked.connect(self.edit_setting)
        self.gridMsgLog.setSelectionBehavior(QTableWidget.SelectRows)
        self.gridMsgLog.setSelectionMode(QTableWidget.SingleSelection)
        self.gridMsgLog.setEditTriggers(QTableWidget.NoEditTriggers)
        self.gridMsgLog.verticalHeader().setDefaultSectionSize(20)
        self.gridMsgLog.setAlternatingRowColors(True)
        self.gridMsgLog.setStyleSheet("alternate-background-color: #e6ffee;")
        self.gridMsgLog.verticalHeader().setVisible(False)
        self.gridMsgLog.doubleClicked.connect(self.show_message)
        
        ex_grid.make_grid(self.gridMsgLog,
                          ['us_id', 'Data', 'Assunto', 'Destinatário', 'Contacto', 'Unidade', 'Tipo', 'Quem Enviou'],
                          [(0, 0), (1, 150), (2, 200), (3, 150), (4, 100), (5, 180), (6, 100), (7, 100)])
        masterLayout.addWidget(self.gridMsgLog)
        if unit_id >= 0:
            self.gridMsgLog.setColumnWidth(5, 0)
            self.filter.append(' msg_unit_id=' + str(unit_id))
        if msg_type >= -1:
            # self.gridMsgLog.setColumnWidth(6,0)
            self.filter.append(' msg_type >-1  ')
        else:
            self.filter.append(' msg_type =  ' + str(msg_type))
        self.refresh_grid()
    
    def refresh_grid(self):
        sql: str = '''select
            msg_id, msg_date_time,msg_subject, msg_to_name,msg_to,un_name ,msg_type_name, msg_who
            from msg_log
            inner join unidades on un_id = msg_log.msg_unit_id
            inner join msg_types on msg_type_id = msg_log.msg_type '''
        if len(self.filter) > 0:
            sql += ' WHERE'
            sql += ' AND '.join(self.filter)
        sql += ' order by msg_id desc'
        xl = libpg.query_many(sql, (True,))
        ex_grid.grid_std(self.gridMsgLog, data=xl, f_col=['i', 't', 's', 's', 's', 's', 's', 's'])
    
    def show_message(self):
        msg_id: int = int(self.gridMsgLog.item(self.gridMsgLog.currentRow(), 0).text())
        sql = '''select *
                from msg_log
                inner join unidades on un_id = msg_log.msg_unit_id
                inner join msg_types on msg_type_id = msg_log.msg_type WHERE msg_log.msg_id = %s'''
        msg_dict = libpg.get_record_dic(sql, (msg_id,))
        if self.gridMsgLog.item(self.gridMsgLog.currentRow(), 6).text() == 'SMS':
            html = liblogos.msg_to_html(msg_dict)
            form = report_display.DisplayReport(html, size=(600, 400))
        form.exec_()
    
    def exit_click(self):
        self.close()


def main():
    app = QApplication(sys.argv)
    form = MsgLogBrowser(0, -1)
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
