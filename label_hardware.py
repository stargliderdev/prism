#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QBrush, QColor, QFont\

from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout, QCheckBox, QPlainTextEdit, QHBoxLayout, QPushButton

import data_sets
import parameters as gl
import qlib as qc


class HardwareLabel(QDialog):
    def __init__(self, hw_id,parent=None):
        super(HardwareLabel, self).__init__(parent)
        masterLayout = QVBoxLayout(self)
        btnLayout = QHBoxLayout()
        self.setWindowTitle('Texto para a Etiqueta')
        self.hw_unit_name = QCheckBox('Nome da Unidade')
        self.hw_unit_name.setChecked(True)
        self.hw_unit_name.stateChanged.connect(self.update_label)
        masterLayout.addLayout(qc.addHLayout([self.hw_unit_name]))
        self.hw_buy_date = QCheckBox('Data de Compra')
        self.hw_buy_date.setChecked(False)
        self.hw_buy_date.stateChanged.connect(self.update_label)
        self.hw_sales_date = QCheckBox('Data de Venda')
        self.hw_sales_date.setChecked(True)
        self.hw_sales_date.stateChanged.connect(self.update_label)
        masterLayout.addLayout(qc.addHLayout([self.hw_buy_date , self.hw_sales_date]))
        self.serial_number = QCheckBox('N/S')
        self.serial_number.setChecked(True)
        self.serial_number.stateChanged.connect(self.update_label)
        masterLayout.addWidget(self.serial_number)
        self.hw_model = QCheckBox('Modelo')
        self.hw_model.setChecked(True)
        self.hw_model.stateChanged.connect(self.update_label)
        
        masterLayout.addWidget(self.hw_model)
        self.preview = QPlainTextEdit()
        palette = QPalette()
        brush = QBrush(QColor(0, 255, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Text, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        brush = QBrush(QColor(0, 255, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        brush = QBrush(QColor(165, 164, 164))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush)
        brush = QBrush(QColor(244, 244, 244))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush)
        font = QFont('courier new', 10)
        font.setWeight(80)
        font.setBold(False)
        self.preview.setPalette(palette)
        masterLayout.addWidget(self.preview)
        self.with_transformer = QCheckBox('C/ Transformador')
        self.with_transformer.stateChanged.connect(self.update_label)
        self.transformer = QCheckBox('Transformador')
        self.transformer.stateChanged.connect(self.update_label)
        self.no_acc = QCheckBox('Sem Acessórios')
        self.no_acc.stateChanged.connect(self.update_label)
        masterLayout.addLayout(qc.addHLayout([self.with_transformer, self.transformer, self.no_acc]))
        toClipboard = QPushButton('Copia')
        toClipboard.clicked.connect(self.copy_to_clipboard_click)
        
        btnLayout.addWidget(toClipboard)
        cancel = QPushButton('Sair')
        cancel.clicked.connect(self.cancel)
        
        btnLayout.addWidget(cancel)
        masterLayout.addLayout(btnLayout)
        self.hardware_dict = data_sets.hardware_to_dict(hw_id)
        self.update_label()
    
        def stateChanged(self, e):
            print(e)
    
    def update_label(self):
        label_text : str = ''
        if self.hw_unit_name.checkState():
            label_text += 'Unidade: ' + self.hardware_dict['un_name'] + '\n'
        if self.hw_model.checkState():
            label_text += 'Modelo: ' + self.hardware_dict['md_name'] + '\n'
        if self.serial_number.checkState():
            label_text += 'N/S: ' + self.hardware_dict['hw_sn'] + '\n'
        if self.hw_buy_date.checkState():
            label_text += 'Compra: ' + self.hardware_dict['hw_supplier_date'].strftime("%d-%d-%Y") + '\n'
        if self.hw_sales_date.checkState():
            label_text += 'Venda: ' + self.hardware_dict['hw_invoice_date'].strftime("%d-%d-%Y") + '\n'
        if self.with_transformer.checkState():
            label_text += 'C/ Transformador \n'
        if self.no_acc.checkState():
            label_text += 'Sem acessórios \n'
        if self.transformer.checkState():
            label_text += 'Transformador \n'
        self.preview.setPlainText(label_text)
        self.cb = QApplication.clipboard()
        
    def copy_to_clipboard_click(self):
        self.cb.setText(self.preview.toPlainText())
    
    def cancel(self):
        self.close()


def main():
    app = QApplication(sys.argv)
    form = HardwareLabel(3303)
    form.show()
    app.exec_()


if __name__ == '__main__':
    gl.conn_string = 'host=192.168.0.250 dbname=prism user=root password=masterkey'
    main()
