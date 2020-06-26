#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from PyQt5.QtWidgets import QDialog, QLabel,  QVBoxLayout, QLineEdit, QPushButton, QToolButton, QDateEdit, QTextEdit, QMessageBox,  QSpinBox,QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from dateutil.relativedelta import relativedelta
import data_sets
import hw_status
import liblogos
import models
import stdio
import libpg
import qlib as qc
import unit_transfer


class HardwareEdit(QDialog):
    def __init__(self, hardwar_dict, parent=None):
        super(HardwareEdit, self).__init__(parent)
        # self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Ficha de Equipamento')
        masterLayout = QVBoxLayout(self)
        # vars
        self.hardware_dict = hardwar_dict
        font = QFont('courier new', 10)
        font.setWeight(80)
        font.setBold(False)
        self.hw_id = QLabel()
        self.hw_id.setMaximumWidth(80)
        self.hw_unit_id = QLabel()
        masterLayout.addLayout(qc.addHLayout([self.hw_id, self.hw_unit_id, True]))
        self.md_name = QLabel()
        self.md_name.setStyleSheet("background-color: #dbf3ff;")
        masterLayout.addLayout(qc.addHLayout(['Modelo:', self.md_name], lw=80))
        self.hw_type_name = QLabel()
        self.hw_type_name.setStyleSheet("background-color: #dbf3ff; ")
        masterLayout.addLayout(qc.addHLayout(['Tipo', self.hw_type_name], lw=80))
        self.hw_sn = QLineEdit()
        self.hw_sn.setFont(font)
        self.hw_sn.setMaxLength(40)
        self.hw_sn.setReadOnly(True)
        self.hw_sn.setStyleSheet("background-color: #dbf3ff;")
        self.hw_sn.textEdited.connect(self.serial_edited)
        
        masterLayout.addLayout(qc.addHLayout(['N/S:', self.hw_sn], lw=80))
        self.hw_status = QLabel()
        self.hw_status.setStyleSheet("background-color: #dbf3ff;")
        hw_status_change = QToolButton()
        hw_status_change.setIcon(QIcon('.//img//edit.png'))
        hw_status_change.clicked.connect(self.hw_status_click)
        masterLayout.addLayout(qc.addHLayout(['Estado:', self.hw_status, hw_status_change, True], lw=80))
        masterLayout.addWidget(qc.HLine())
        self.unitNameLb = QLabel()
        self.unitNameLb.setMaximumWidth(200)
        unitChangeTBt = QToolButton()
        unitChangeTBt.setIcon(QIcon('.//img//change_unit.png'))
        masterLayout.addLayout(qc.addHLayout(['Unidade:', self.unitNameLb, True, unitChangeTBt], lw=80))
        self.hw_function = QLineEdit()
        self.hw_function.setMaxLength(20)
        self.hw_function.setMaximumWidth(200)
        masterLayout.addLayout(qc.addHLayout(['Função:', self.hw_function, True], lw=80))
        masterLayout.addWidget(qc.HLine())
        self.hw_invoice_date = QDateEdit()
        self.hw_invoice_date.setMaximumWidth(100)
        self.hw_invoice_date.setDisplayFormat("dd.MM.yyyy")
        self.hw_invoice = QLineEdit()
        self.hw_invoice.setMaxLength(10)
        self.hw_invoice.setMaximumWidth(100)
        self.hw_warranty = QSpinBox()
        self.hw_warranty.setMaximumWidth(70)
        self.hwSellAgeLabel = QLabel()
        self.hwSellAgeLabel.setStyleSheet("color: #FF10ff;")
        masterLayout.addLayout(qc.addHLayout(['Doc. Venda:', self.hw_invoice, 'Data:', self.hw_invoice_date, 'Garantia:', self.hw_warranty, True], lw=80))
        masterLayout.addLayout(qc.addHLayout(['I. Venda:', self.hwSellAgeLabel]))
        masterLayout.addWidget(qc.HLine())
        self.hw_supplier = QLineEdit()
        self.hw_supplier.setMaxLength(40)
        self.hw_supplier.setMaximumWidth(200)
        masterLayout.addLayout(qc.addHLayout(['Fornecedor:', self.hw_supplier, True], lw=80))
        self.hw_supplier_date = QDateEdit()
        self.hw_supplier_date.setMaximumWidth(100)
        self.hw_supplier_date.setDisplayFormat("dd.MM.yyyy")
        self.hw_invoice_supplier = QLineEdit()
        self.hw_invoice_supplier.setMaxLength(10)
        self.hw_invoice_supplier.setMaximumWidth(100)
        self.hw_supplier_warranty = QSpinBox()
        self.hw_supplier_warranty.setMaximumWidth(70)
        masterLayout.addLayout(qc.addHLayout(['Factura:', self.hw_invoice_supplier, 'Data:', self.hw_supplier_date, 'Garantia',
                                              self.hw_supplier_warranty, True], lw=80))

        self.hwBuyAgeLabel = QLabel()
        self.hwBuyAgeLabel.setStyleSheet("color: #FF10ff;")
        masterLayout.addLayout(qc.addHLayout(['I. Compra:', self.hwBuyAgeLabel]))
        self.hw_obs = QTextEdit()
        self.hw_obs.setMaximumHeight(200)
        masterLayout.addWidget(self.hw_obs)
        saveBtn = QPushButton('Guardar')
        saveBtn.clicked.connect(self.save_click)
        exitBtn = QPushButton('Sair')
        exitBtn.clicked.connect(self.exit_click)
        masterLayout.addLayout(qc.addHLayout([saveBtn, exitBtn]))
        if self.hardware_dict['hw_id'] == -1:
            form = models.ModelsBrowser({'mode': 1})
            form.exec_()
            if 'brand_name' in form.ret:
                self.hardware_dict['md_name'] = form.ret['brand_name'] + ' ' + form.ret['model_name']
                self.hardware_dict['model_id'] = form.ret['model_id']
                self.hardware_dict['hw_type_name'] = form.ret['hw_type_name']
                self.hw_sn.setReadOnly(False)
                self.hw_sn.setStyleSheet("background-color: #00ff00;")
                self.init_form()
                self.refresh_form()
            else:
                saveBtn.setEnabled(False)
        else:
            self.hardware_dict = data_sets.hardware_to_dict(self.hardware_dict['hw_id'])
            unitChangeTBt.clicked.connect(self.hw_change_unit)
            self.refresh_form()
        
    def hw_status_click(self):
        form = hw_status.HardwareStatus()
        form.exec_()
        if form.ret[0]:
            self.hw_status.setText(form.ret[1])
            if form.ret[2] == 0:
                self.hardware_dict['hw_unit_id'] = 0 # em stock
            if form.ret[2] == 3:
                self.hardware_dict['hw_unit_id'] = 99999  # emprestimo
                
    def hw_change_unit(self):
        form = unit_transfer.HardwareTransfer(self.hardware_dict)
        form.exec_()
        if form.ret:
            self.close()
        
    def init_form(self):
        self.hardware_dict['hw_id'] = -1
        self.hardware_dict['hw_sn'] = ''
        self.hardware_dict['hw_status_name'] = 'Activo'
        self.hardware_dict['hw_status_id'] = 2
        self.hardware_dict['hw_function'] = ''
        self.hardware_dict['hw_invoice'] = 'n/a'
        self.hardware_dict['hw_invoice_date'] = datetime.datetime(2012, 0o1, 0o1)
        self.hardware_dict['hw_warranty'] = 0
        self.hardware_dict['hw_supplier'] = 'n/a'
        self.hardware_dict['hw_supplier_warranty'] = 0
        if 'un_name' in self.hardware_dict:
            pass
        else:
            self.hardware_dict['un_name'] = ''
        self.hardware_dict['hw_supplier_date'] = datetime.datetime(2012, 0o1, 0o1)  # datetime.datetime.now()
        self.hardware_dict['hw_invoice_supplier'] = 'n/a'
        self.hardware_dict['hw_obs'] = ''
    
    def refresh_form(self):
        self.hw_id.setText(str(self.hardware_dict['hw_id']) + '-' + '{0:x}'.format(self.hardware_dict['hw_id']).upper())
        self.md_name.setText(self.hardware_dict['md_name'])
        self.hw_type_name.setText(self.hardware_dict['hw_type_name'])
        self.hw_sn.setText(self.hardware_dict['hw_sn'])
        self.hw_status.setText(self.hardware_dict['hw_status_name'])
        self.hw_function.setText(self.hardware_dict['hw_function'])
        self.hw_invoice.setText(self.hardware_dict['hw_invoice'])
        try:
            self.hw_invoice_date.setDate(self.hardware_dict['hw_invoice_date'])
        except TypeError:
            self.hw_invoice_date.setDate(datetime.datetime.now() - relativedelta(years=10))
        self.hw_warranty.setValue(self.hardware_dict['hw_warranty'])
        self.hw_supplier.setText(self.hardware_dict['hw_supplier'])
        try:
            self.hw_supplier_date.setDate(self.hardware_dict['hw_supplier_date'])
        except TypeError:
            self.hw_supplier_date.setDate(datetime.datetime.now() - relativedelta(years=10))
        self.hw_invoice_supplier.setText(self.hardware_dict['hw_invoice_supplier'])
        self.unitNameLb.setText(self.hardware_dict['un_name'])
        self.hw_supplier_warranty.setValue(self.hardware_dict['hw_supplier_warranty'])
        self.hw_obs.setText(self.hardware_dict['hw_obs'])
        self.hwSellAgeLabel.setText(td_format(datetime.datetime.today().date() - self.hw_invoice_date.date().toPyDate()))
        self.hwBuyAgeLabel.setText(td_format(datetime.datetime.today().date() - self.hw_supplier_date.date().toPyDate()))
        
    def insert_record(self):
        a = ()
        sql = '''insert into hardware(
        hw_model_id, hw_sn, hw_unit_id, hw_function, hw_invoice, hw_invoice_date, hw_supplier,
        hw_warranty, hw_supplier_date, hw_invoice_supplier, hw_supplier_warranty, hw_obs, hw_status_id)
        VALUES (%s,%s,%s, %s,%s,%s, %s,%s,%s, %s,%s,%s, 1) '''
        data = (self.hardware_dict['model_id'],)
        data += (str(stdio.write_field(self.hw_sn)).upper(),)
        data += (self.hardware_dict['hw_unit_id'],)
        data += (stdio.write_field(self.hw_function),)
        data += (stdio.write_field(self.hw_invoice),)
        data += (stdio.write_field(self.hw_invoice_date),)
        data += (stdio.write_field(self.hw_supplier),)
        data += (stdio.write_field(self.hw_warranty),)
        data += (stdio.write_field(self.hw_supplier_date),)
        data += (stdio.write_field(self.hw_invoice_supplier),)
        data += (stdio.write_field(self.hw_supplier_warranty),)
        data += (stdio.write_field(self.hw_obs),)
        libpg.execute_query(sql, data)
        liblogos.hardware_update_settings(self.hardware_dict['hw_unit_id'])
        self.close()
    
    def update_record(self):
        sql = '''UPDATE hardware set
        hw_unit_id=%s,
        hw_function=%s,
        hw_invoice=%s,
        hw_invoice_date=%s,
        hw_warranty=%s,
        hw_supplier=%s,
        hw_supplier_date=%s,
        hw_model_id=%s,
        hw_invoice_supplier=%s,
        hw_supplier_warranty=%s,
        hw_obs=%s,
        hw_status_id=(select hwd_status_id from hw_status where lower(hwd_status_name) = %s)
        WHERE hw_id= %s'''
        data = (self.hardware_dict['hw_unit_id'],)
        data += (stdio.write_field(self.hw_function),)
        data += (stdio.write_field(self.hw_invoice),)
        data += (stdio.write_field(self.hw_invoice_date),)
        data += (stdio.write_field(self.hw_warranty),)
        data += (stdio.write_field(self.hw_supplier),)
        data += (stdio.write_field(self.hw_supplier_date), self.hardware_dict['hw_model_id'])
        data += (stdio.write_field(self.hw_invoice_supplier),)
        data += (stdio.write_field(self.hw_supplier_warranty),)
        data += (stdio.write_field(self.hw_obs),)
        data += (self.hw_status.text().lower(),)
        data += (self.hardware_dict['hw_id'],)
        libpg.execute_query(sql, data)
        liblogos.hardware_update_settings(self.hardware_dict['hw_unit_id'])
    
    def exit_click(self):
        self.close()
    
    def save_click(self):
        if self.hardware_dict['hw_id'] == -1:
            a = libpg.query_one('select hw_id from hardware where hw_sn = %s', (self.hw_sn.text().upper(),))
            if a is None:
                self.insert_record()
            else:
                QMessageBox.critical(None,"Pesquisa de Numero de Série","O numero de série já existe na Base de Dados",
                                     QMessageBox.StandardButtons(QMessageBox.Close), QMessageBox.Close)
        else:
            self.update_record()
            self.close()

    def serial_edited(self):
        a = self.hw_sn.text().upper()
        a = a.replace('-','')
        a = a.replace('.','')
        a = a.replace('(','')
        a = a.replace(')','')
        a = a.replace('/','')
        a = a.replace(',','')
        a = a.replace('#','')
        a = a.replace(' ','')
        a = a.replace('_','')
        a = a.replace('[','')
        a = a.replace(']','')
        self.hw_sn.setText(a)


def td_format(td_object):
    seconds = int(td_object.total_seconds())
    periods = [
        ('ano',        60*60*24*365),
        ('mese',       60*60*24*30),
        ('dia',        60*60*24),
        ('hour',        60*60),
        ('minute',      60),
        ('second',      1)
    ]
    strings = []
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value , seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append("%s %s%s" % (period_value, period_name, has_s))
    return ", ".join(strings)


if __name__ == '__main__':
    pass
