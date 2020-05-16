#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import pprint

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QBrush, QColor, QFont
from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout, QCheckBox, QPlainTextEdit, QHBoxLayout, QPushButton

import data_sets
import parameters as gl
import qlib as qc


class ProcessLabel(QDialog):
    def __init__(self, proc_id, parent=None):
        super(ProcessLabel, self).__init__(parent)
        masterLayout = QVBoxLayout(self)
        btnLayout = QHBoxLayout()
        self.setWindowTitle('Texto para a Etiqueta')
        self.unitNameCkb = QCheckBox('Nome da Unidade')
        self.unitNameCkb.setChecked(True)
        self.unitNameCkb.stateChanged.connect(self.update_label)
        masterLayout.addLayout(qc.addHLayout([self.unitNameCkb]))
        self.dateProcCkb = QCheckBox('Data')
        self.dateProcCkb.setChecked(True)
        self.dateProcCkb.stateChanged.connect(self.update_label)
        self.procCkb = QCheckBox('Prcesso')
        self.procCkb.setChecked(True)
        self.procCkb.stateChanged.connect(self.update_label)
        masterLayout.addLayout(qc.addHLayout([self.dateProcCkb, self.procCkb]))
        self.serialNumberCkb = QCheckBox('N/S')
        self.serialNumberCkb.setChecked(True)
        self.serialNumberCkb.stateChanged.connect(self.update_label)
        masterLayout.addWidget(self.serialNumberCkb)
        self.procModelCkb = QCheckBox('Modelo')
        self.procModelCkb.setChecked(True)
        self.procModelCkb.stateChanged.connect(self.update_label)
        self.procReportedChk = QCheckBox('Avaria')
        self.procReportedChk.setChecked(True)
        self.procReportedChk.stateChanged.connect(self.update_label)

        masterLayout.addWidget(self.procModelCkb)
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
        self.with_transformer = QCheckBox('c/ Transformador')
        self.with_transformer.stateChanged.connect(self.update_label)
        self.cablesChk = QCheckBox('c/ Cabos')
        self.cablesChk.stateChanged.connect(self.update_label)
        self.no_acc = QCheckBox('Sem Acessórios')
        self.no_acc.stateChanged.connect(self.update_label)
        masterLayout.addLayout(qc.addHLayout([self.with_transformer, self.cablesChk, self.no_acc]))
        toClipboard = QPushButton('Copia')
        toClipboard.clicked.connect(self.copy_to_clipboard_click)
        
        btnLayout.addWidget(toClipboard)
        cancel = QPushButton('Sair')
        cancel.clicked.connect(self.cancel)
        
        btnLayout.addWidget(cancel)
        masterLayout.addLayout(btnLayout)
        self.proc_dict = data_sets.process_to_dict(proc_id)
        self.update_label()
    
    def update_label(self):
        label_text: str = ''
        label_text += '#: ' + str(self.proc_dict['proc_id']) + '\n'
        if self.dateProcCkb.checkState():
            label_text += 'Data: ' + self.proc_dict['proc_date'].strftime("%d-%d-%Y") + '\n'
        if self.unitNameCkb.checkState():
            label_text += 'Unidade: ' + self.proc_dict['proc_unit_name'] + '\n'
        if self.procModelCkb.checkState():
            label_text += 'Modelo: ' + self.proc_dict['proc_model'] + '\n'
        if self.serialNumberCkb.checkState():
            label_text += 'N/S: ' + self.proc_dict['proc_serial_number'] + '\n'
        if self.procReportedChk.checkState():
            label_text += '--------------------------\n'
            label_text += self.proc_dict['proc_reported'] + '\n'
        
        if self.with_transformer.checkState():
            label_text += 'Transformador \n'
        if self.no_acc.checkState():
            label_text += 'Sem acessórios \n'
        if self.cablesChk.checkState():
            label_text += 'Cabos \n'
        self.preview.setPlainText(label_text)
        self.cb = QApplication.clipboard()
    
    def copy_to_clipboard_click(self):
        self.cb.setText(self.preview.toPlainText())
    
    def cancel(self):
        self.close()


def main():
    app = QApplication(sys.argv)
    form = ProcessLabel(19404)
    form.show()
    app.exec_()


if __name__ == '__main__':
    gl.conn_string = 'host=192.168.0.250 dbname=prism user=root password=masterkey'
    main()
