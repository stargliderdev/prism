#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, \
    QToolButton, QMessageBox, QListWidget, QWidget, QTableWidget, QCheckBox, \
    QApplication, QHBoxLayout,QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

import liblogos
import stdio
import libpg
import qlib
import cp
import parameters as gl


class EditClient(QDialog):
    def __init__(self,  client_id, parent = None):
        super(EditClient,  self).__init__(parent)
        self.resize(600, 400)
        self.ret = (False,'')
        self.setWindowTitle('Edita Cliente')
        masterLayout = QVBoxLayout(self)
        ok_Btn = QPushButton('Grava')
        ok_Btn.setMinimumWidth(60)
        ok_Btn.clicked.connect(self.save_click)
        
        cancela_Btn = QPushButton('Sair')
        cancela_Btn.setMinimumWidth(60)
        cancela_Btn.clicked.connect(self.exit_click)

        deactivet = QPushButton('Desactivar')
        deactivet.setMinimumWidth(60)
        deactivet.clicked.connect(self.deactive_click)
        masterLayout.addLayout(qlib.addHLayout([ok_Btn,True,deactivet, cancela_Btn]))

        self.client_id = client_id
        self.cl_id = QLineEdit()
        self.cl_id.setAlignment(Qt.AlignRight)
        self.cl_id.setMaximumWidth(60)
        self.cl_id.setReadOnly(True)
        self.cl_id.setStyleSheet("background-color: #dbf3ff;")
        self.units_drill = QToolButton()
        self.units_drill.setIcon(QIcon('.//img//drill_down.png'))
        self.units_drill.setToolTip('Ver Unidades')
        self.units_drill.clicked.connect(self.goto_units_click)

        self.cl_nif = QLineEdit()
        self.cl_nif.setMaxLength(9)
        self.cl_nif.setMaximumWidth(100)
        self.cl_ccEdit = QLineEdit()
        self.cl_ccEdit.setAlignment(Qt.AlignRight)
        self.cl_ccEdit.setReadOnly(True)
        self.cl_ccEdit.setMaximumWidth(90)
        masterLayout.addLayout(qlib.addHLayout(['N.I.F.:', self.cl_nif, self.cl_id,self.units_drill,True,'Conta Corrente', self.cl_ccEdit], lw=120))

        self.cl_nome = QLineEdit()
        self.cl_nome.setMaxLength(50)
        masterLayout.addLayout(qlib.addHLayout(['D. Social:', self.cl_nome], lw=120))

        self.cl_comercial_name = QLineEdit()
        self.cl_comercial_name.setMaxLength(100)
        masterLayout.addLayout(qlib.addHLayout(['N. Comercial:', self.cl_comercial_name], lw=120))

        self.cl_cap_social = QLineEdit()
        self.cl_cap_social.setMaxLength(15)
        self.cl_cap_social.setAlignment(Qt.AlignRight)
        self.cl_cap_social.setMaximumWidth(130)

        self.cl_conservatoria = QLineEdit()
        self.cl_conservatoria.setMaxLength(100)
        masterLayout.addLayout(qlib.addHLayout(['Conservatória:', self.cl_conservatoria,'Cap. Social:', self.cl_cap_social], lw=120))

        self.cl_morada = QLineEdit()
        self.cl_morada.setMaxLength(255)
        masterLayout.addLayout(qlib.addHLayout(['Morada:', self.cl_morada], lw=120))

        self.cl_localidade = QLineEdit()
        self.cl_localidade.setMaxLength(45)
        masterLayout.addLayout(qlib.addHLayout(['Localidade:', self.cl_localidade], lw=120))

        self.cl_cp = QLineEdit()
        # self.cl_cp.setMaximumWidth(350)
        self.cl_cp.setReadOnly(True)
        self.cl_cp.setStyleSheet("background-color: #dbf3ff;")
        cp_drill_down = QToolButton()
        cp_drill_down.setIcon(QIcon('.//img//drill_down.png'))
        cp_drill_down.setToolTip('Procurar Código Postal')
        cp_drill_down.clicked.connect(self.cp_drill_down_click)
        
        masterLayout.addLayout(qlib.addHLayout(['Código Postal:', self.cl_cp, cp_drill_down], lw=120))

        self.cl_telefone = QLineEdit()
        self.cl_telefone.setMaxLength(30)
        masterLayout.addLayout(qlib.addHLayout(['Telefones:', self.cl_telefone], lw=120))

        self.cl_email = QLineEdit()
        self.cl_email.setMaxLength(30)
        masterLayout.addLayout(qlib.addHLayout(['e-mail:', self.cl_email], lw=120))
        self.unitsInClientGrid = QTableWidget()
        self.unitsInClientGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.unitsInClientGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.unitsInClientGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.unitsInClientGrid.verticalHeader().setDefaultSectionSize(20)
        self.unitsInClientGrid.setAlternatingRowColors(True)
        self.unitsInClientGrid.setStyleSheet("alternate-background-color: #e6ffee;")
        self.unitsInClientGrid.verticalHeader().setVisible(False)
        self.unitsInClientGrid.setMinimumHeight(100)

        masterLayout.addWidget(self.unitsInClientGrid)
        if self.client_id == -1:
            self.units_drill.setEnabled(False)
            deactivet.setVisible(False)
        else:
            self.get_data(client_id)
            self.cl_nif.setReadOnly(True)
            self.cl_nif.setStyleSheet("background-color: #dbf3ff;")
            self.refresh_form()
            self.refresh_grid()
            liblogos.log_actions(gl.user_dict, 'view client', 'cliente: ' + str(stdio.write_field(self.cl_nif)) + ' ' + stdio.write_field(self.cl_nome))
        
    def refresh_grid(self):
        sql = '''select un_id, un_name, unidades.un_activa
                from unidades
                where un_cliente_id =%s order by un_name'''
        units_in_client = libpg.query_many(sql, (self.client_id,))
    
        self.unitsInClientGrid.setColumnCount(3)
        self.unitsInClientGrid.setRowCount(len(units_in_client))
        self.unitsInClientGrid.setHorizontalHeaderLabels(['#','Nome', 'Estado'])
        self.unitsInClientGrid.setColumnWidth(0,50)
        self.unitsInClientGrid.setColumnWidth(1,280)
        self.unitsInClientGrid.setColumnWidth(2,70)
        line = 0
        for n in units_in_client:
            item = QTableWidgetItem()
            item.setText(str(n[0]))
            item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self.unitsInClientGrid.setItem(line,0, item)
            item = QTableWidgetItem()
            item.setText(n[1])
            self.unitsInClientGrid.setItem(line, 1, item)
            item = QTableWidgetItem()
            if n[2]:
                item.setIcon(QIcon('.//img//sms_ticket.png'))
            else:
                item.setIcon(QIcon('.//img//deactivate.png'))
            self.unitsInClientGrid.setItem(line,2, item)
            line += 1
            
    def goto_units_click(self):
        self.ret = (True,)
        self.close()

    def save_click(self):
        if self.client_id == -1:
            a = self.validate_form()
            if a[0]:
                self.insert_record()
                self.ret = (False,)
                self.close()
        else:
            self.update_record()
            self.ret = (False,)
            self.close()

    def deactive_click(self):
        res = QMessageBox.question(self,
                self.tr("Desactivar Cliente"),    self.tr("""Pretendes desactivar este cliente?"""),
                QMessageBox.StandardButtons(QMessageBox.Cancel|QMessageBox.Ok))
        if res == QMessageBox.Ok:
            libpg.execute_query('update clientes set cl_active = False where cl_id = %s', (self.customer_dict['cl_id'],))
            self.order = 0
            self.close()

    def cp_drill_down_click(self):
        form = cp.CpSearch()
        form.exec_()
        if form.ret[0]:
            self.cl_morada.setText(form.ret[1])
            self.cl_cp.setText(form.ret[2])
            self.cl_localidade.setText(form.ret[3])

    def exit_click(self):
        self.order = 0
        self.close()

    def get_data(self, id):
        self.customer_dict = libpg.get_record_dic('SELECT * from clientes where cl_id  = %s', (id,))

    def validate_form(self):
        b = (True,)
        if self.cl_nif.text() == '':
            b = (False, 'Sem NIF')
        elif self.cl_nome.text() == '':
            b = (False, 'Sem Nome')
        elif self.cl_morada.text() == '':
            b = (False, 'Sem Morada')
        elif self.cl_localidade.text() == '':
            b = (False, 'Sem Localidade')
        elif self.cl_cp.text() == '':
            b = (False, 'Sem Código Postal')

        if b[0]:
            if libpg.query_one('select cl_id from clientes where cl_nif=%s', (str(self.cl_nif.text()),)) is None:
                pass
            else:
                b = (False, 'NIF duplicado')
            # if libpg.query_one('select cl_id from clientes where cl_id=%s', (int(self.cl_id.text()),)) is None:
            #     pass
            # else:
            #     b = (False, 'Numero externo duplicado')
        if not b[0]:
            QMessageBox.critical(None,"Erro de entrada de dados",b[1])
            return b
        else:
            return b

    def refresh_form(self):
        stdio.read_field(self.cl_id,'cl_id', self.customer_dict)
        stdio.read_field(self.cl_nif,'cl_nif', self.customer_dict)
        stdio.read_field(self.cl_nome,'cl_nome', self.customer_dict)
        stdio.read_field(self.cl_morada,'cl_morada', self.customer_dict)
        stdio.read_field(self.cl_localidade,'cl_localidade', self.customer_dict)
        stdio.read_field(self.cl_cp,'cl_cp', self.customer_dict)
        stdio.read_field(self.cl_telefone,'cl_telefone', self.customer_dict)
        stdio.read_field(self.cl_email,'cl_email', self.customer_dict)
        stdio.read_field(self.cl_comercial_name,'cl_comercial_name', self.customer_dict)
        stdio.read_field(self.cl_conservatoria,'cl_conservatoria', self.customer_dict)
        stdio.read_field(self.cl_cap_social,'cl_cap_social', self.customer_dict)
        stdio.read_field(self.cl_ccEdit,'cl_cc', self.customer_dict)

    def insert_record(self):
        sql = '''insert into clientes(
        cl_nif, cl_nome, cl_morada, cl_localidade, cl_cp, cl_telefone, cl_email, cl_comercial_name, cl_conservatoria,
        cl_cap_social
         ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        data = ()
        data += (stdio.write_field(self.cl_nif),)
        data += (stdio.write_field(self.cl_nome),)
        data += (stdio.write_field(self.cl_morada),)
        data += (stdio.write_field(self.cl_localidade),)
        data += (stdio.write_field(self.cl_cp),)
        data += (stdio.write_field(self.cl_telefone),)
        data += (stdio.write_field(self.cl_email),)
        data += (stdio.write_field(self.cl_comercial_name),)
        data += (stdio.write_field(self.cl_conservatoria),)
        data += (stdio.write_field(self.cl_cap_social),)
        libpg.execute_query(sql, data)
        liblogos.log_actions(gl.user_dict, 'insert client', 'cliente: ' + str(stdio.write_field(self.cl_nif)) + ' ' + stdio.write_field(self.cl_nome))
        
    def update_record(self):
        sql = '''UPDATE clientes SET
        cl_nome=%s,
        cl_morada=%s,
        cl_localidade=%s,
        cl_cp=%s,
        cl_telefone=%s,
        cl_email=%s,
        cl_comercial_name=%s,
        cl_conservatoria=%s,
        cl_cap_social=%s
        WHERE cl_id = %s'''
        data = ()
        data += (stdio.write_field(self.cl_nome),)
        data += (stdio.write_field(self.cl_morada),)
        data += (stdio.write_field(self.cl_localidade),)
        data += (stdio.write_field(self.cl_cp),)
        data += (stdio.write_field(self.cl_telefone),)
        data += (stdio.write_field(self.cl_email),)
        data += (stdio.write_field(self.cl_comercial_name),)
        data += (stdio.write_field(self.cl_conservatoria),)
        data += (stdio.write_field(self.cl_cap_social),  self.client_id)
        libpg.execute_query(sql, data)
        liblogos.log_actions(gl.user_dict, 'update client', 'cliente: ' + str(stdio.write_field(self.cl_nif)) + ' ' + stdio.write_field(self.cl_nome))


def main():
    app = QApplication(sys.argv)
    form = EditClient(87)
    form.show()
    app.exec_()
    print(form.ret)


if __name__ == '__main__':
    main()
