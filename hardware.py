#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QTableWidget, QToolButton, QApplication, QComboBox, QLabel, \
    QPushButton
from PyQt5.QtGui import QIcon
# from matplotlib import pyplot as plt
import sys

import label_hardware
import libpg
import models
import qlib as qc
import ex_grid
import hardware_edit
import report_display
import report_lib


class HardwareBrw(QDialog):
    def __init__(self, conf, parent=None):
        super(HardwareBrw, self).__init__(parent)
        self.resize(1024, 768)
        mainTabLayout = QVBoxLayout(self)
        self.setWindowTitle('Equipamentos')
        self.settings = conf
        self.hw_status = QComboBox()
        self.hw_status.addItems(['Stock', 'Activo', 'Abatido','Emprestimo','Todos'])
        self.hw_status.setCurrentIndex(1)
        self.hw_status.currentIndexChanged.connect(self.hw_status_change)
        self.hwReportCbx = QComboBox()
        self.hwReportCbx.addItems(['', 'Lista Idades', 'Conferencia'])
        self.hwReportCbx.setCurrentIndex(0)
        self.hwReportCbx.currentIndexChanged.connect(self.report_change)
        make_label = QToolButton()
        make_label.setIcon(QIcon('.//img//barcode.png'))
        make_label.clicked.connect(self.make_label_click)
        
        search_button = QToolButton()
        search_button.setIcon(QIcon('.//img//search_sn.png'))
        search_button.clicked.connect(self.hw_by_serial_number)
        filterBtn = QToolButton()
        filterBtn.setIcon(QIcon('.//img//search_hw.png'))
        filterBtn.clicked.connect(self.get_models_click)

        self.filter_label = QLabel('')
        self.filter_label.setMinimumWidth(300)
        self.filter_label.setMaximumWidth(300)
        filter_cleanBtn = QToolButton()
        filter_cleanBtn.clicked.connect(self.filter_clean_click)
        closeBtn = QPushButton()
        closeBtn.setText('Sair')
        closeBtn.setFocusPolicy(0)  # Qt.NoFocus
        closeBtn.clicked.connect(self.exit_click)
        self.serialNumberEdt = QLineEdit()
        self.serialNumberEdt.setMaximumWidth(300)
        self.serialNumberEdt.returnPressed.connect(self.hw_by_serial_number)
        add_old_hw_unit = QPushButton()
        add_old_hw_unit.setText('Adiciona Equi.')
        if self.settings['unit_id'] > 0:
            mainTabLayout.addLayout(qc.addHLayout([add_old_hw_unit, 'Estado', self.hw_status, True, 'Relatórios', self.hwReportCbx, make_label,True, closeBtn]))
            add_old_hw_unit.clicked.connect(self.add_old_hw_click)
        elif self.settings['model_id'] > 0:
            mainTabLayout.addLayout(qc.addHLayout(['Estado', self.hw_status, True, 'Relatórios', self.hwReportCbx, make_label,True, closeBtn]))
        else:
            mainTabLayout.addLayout(qc.addHLayout(['N/S',self.serialNumberEdt, search_button, 'Estado', self.hw_status,make_label, True,closeBtn]))
            mainTabLayout.addLayout(qc.addHLayout(['Modelo',self.filter_label, filterBtn,filter_cleanBtn,True]))
        self.grid_hardware = QTableWidget()
        self.grid_hardware.setSelectionBehavior(QTableWidget.SelectRows)
        self.grid_hardware.setSelectionMode(QTableWidget.SingleSelection)
        self.grid_hardware.setEditTriggers(QTableWidget.NoEditTriggers)
        self.grid_hardware.verticalHeader().setDefaultSectionSize(20)
        self.grid_hardware.setAlternatingRowColors(True)
        self.grid_hardware.setStyleSheet("alternate-background-color: #e6f2ff;")
        self.grid_hardware.verticalHeader().setVisible(False)
        self.grid_hardware.resizeColumnsToContents()
        ex_grid.make_grid(self.grid_hardware, headers=['ID', 'Tipo', 'Marca','Modelo', 'SN', 'Estado', 'un_id', 'Unidade'],
                          col_width=[(0, 0), (1, 150),(2, 150), (3, 150), (4, 150), (5, 90), (6, 0), (7, 300)])
        self.grid_hardware.itemDoubleClicked.connect(self.edit_hardware)
        self.grid_hardware.setColumnHidden(0, True)
        self.grid_hardware.setColumnHidden(6, True)
        mainTabLayout.addWidget(self.grid_hardware)
        if self.settings['unit_id'] > 0 or self.settings['model_id'] > 0:
            self.hw_status.setCurrentIndex(4)
            if self.settings['unit_id'] > 0:
                self.setWindowTitle('Equipamentos na unidade ' + self.settings['un_name'])
        search_button.setFocus()

    def exit_click(self):
        self.close()
    
    def make_sql_filter(self):
        order_by = ' ASC'
        order_by_field = ' hw_type_order '
        if self.hw_status.currentIndex() < 4:
            status = ' hw_status_id=' + str(self.hw_status.currentIndex())
        else:
            status = ' hw_status_id >-1 '
        if self.settings['unit_id'] > 0:
            unit_drill = ' AND hardware.hw_unit_id = ''' + str(self.settings['unit_id'])
        else:
            unit_drill = ''
        if self.settings['model_id'] > 0:
            model_drill = ' AND hw_model_id=''' + str(self.settings['model_id'])
        else:
            model_drill = ''
        if not self.serialNumberEdt.text() == '':
            serial_search = ''' AND hw_sn  LIKE \'%%''' + self.serialNumberEdt.text().upper().strip() + '''%%\''''
        else:
            serial_search = ''
        
        sql = '''SELECT hardware.hw_id, hw_type_name, brands.br_name , models.md_name, hw_sn, hwd_status_name,hw_unit_id, un_name
                     FROM hardware, models, hw_status, brands, unidades, hardware_types
                     WHERE brands.br_active=TRUE AND ''' + status + unit_drill + model_drill + serial_search +\
              '''    AND unidades.un_id=hardware.hw_unit_id AND
              hw_type_id = md_hardware_type AND
              hardware.hw_model_id = models.md_id AND hw_status.hwd_status_id = hardware.hw_status_id
              AND models.md_brand_id = brands.br_id ORDER BY ''' + order_by_field + order_by
        return sql
    
    def show_inventory_click(self):
        sql = self.make_sql_filter()
        bc = libpg.query_many(sql, (True,))
        ex_grid.grid_std(self.grid_hardware, data=bc, f_col=['i', 's','s', 's', 's', 's', 'i', 's'])
    
    def hw_status_change(self):
        sql = self.make_sql_filter()
        bc = libpg.query_many(sql)
        ex_grid.grid_std(self.grid_hardware, data=bc, f_col=['i', 's','s', 's', 's', 's', 'i', 's'])
    
    def hw_by_serial_number(self):
        self.hw_status.setCurrentIndex(4)
        self.settings['model_id'] = 0
        self.settings['unit_id'] = 0
        sql = self.make_sql_filter()
        bc = libpg.query_many(sql, (True,))
        ex_grid.grid_std(self.grid_hardware, data=bc, f_col=['i', 's','s', 's', 's', 's', 'i', 's'])
    
    def get_models_click(self):
        self.serialNumberEdt.setText('')
        form = models.ModelsBrowser({'mode': 1})
        form.exec_()
        self.settings.update(form.ret)
        sql = self.make_sql_filter()
        bc = libpg.query_many(sql, (True,))
        ex_grid.grid_std(self.grid_hardware, data=bc, f_col=['i', 's','s', 's', 's', 's', 'i', 's'])
        try:
            self.filter_label.setText(self.settings['brand_name'] + ' ' + self.settings['model_name'])
        except KeyError:
            pass
        
    def hw_filter_unit(self):
        sql = self.make_sql_filter()
        bc = libpg.query_many(sql, (True,))
        ex_grid.grid_std(self.grid_hardware, data=bc, f_col=['i', 's','s', 's', 's', 's', 'i', 's'])
    
    def filter_clean_click(self):
        self.filter_label.setText('')
        bc = []
        ex_grid.grid_std(self.grid_hardware, data=bc, f_col=['i', 's','s', 's', 's', 's', 'i', 's'])
    
    def edit_hardware(self):
        hw_id = self.grid_hardware.item(self.grid_hardware.currentRow(), 0).text().upper()
        form = hardware_edit.HardwareEdit({'hw_id': hw_id})
        form.exec_()
        self.hw_status_change()
    
    def report_change(self):
        choice = self.hwReportCbx.currentIndex()
        self.hwReportCbx.setCurrentIndex(0)
        if choice == 1:
            self.make_ages_report()
        elif choice == 2:
            self.make_inventory_report()
      
    def make_label_click(self):
        try:
            hw_id = self.grid_hardware.item(self.grid_hardware.currentRow(), 0).text().upper()
            form = label_hardware.HardwareLabel(hw_id)
            form.exec_()
        except AttributeError:
            pass
    
    def make_ages_report(self):
        sql = '''SELECT hardware.hw_id, brands.br_name , models.md_name, hardware.hw_sn,
                    case
                    when now()::date - hw_invoice_date::date <= 365 then '< 1 ano'
                    when now()::date - hw_invoice_date::date > 365 and now()::date - hw_invoice_date::date <=730 then '< 2 anos'
                    when now()::date - hw_invoice_date::date > 730 and now()::date - hw_invoice_date::date <=1825 then '5 anos'
                    when now()::date - hw_invoice_date::date > 1825 and now()::date - hw_invoice_date::date <=2555 then '7 anos'
                    when now()::date - hw_invoice_date::date > 2555 then '+ 7 anos'
                    end as det,hwd_status_name, hw_type_name
                FROM hardware, models, hw_status, brands, unidades, hardware_types
                WHERE un_id=%s AND unidades.un_id=hardware.hw_unit_id and
                    hw_type_id=models.md_hardware_type and
                    hardware.hw_model_id = models.md_id AND hw_status.hwd_status_id = hardware.hw_status_id
                    AND models.md_brand_id = brands.br_id ORDER BY  md_name '''
        data_set = libpg.query_many(sql, (self.settings['unit_id'],))
        
        proc_html = report_lib.hardware_ages_report(data_set)
        form = report_display.DisplayReport(proc_html)
        form.exec_()

    def make_inventory_report(self):
        sql = '''SELECT hw_id,'☐', hw_type_name, brands.br_name , md_name, hw_sn
                FROM hardware, models, hw_status, brands, unidades, hardware_types
                WHERE un_id=%s AND unidades.un_id=hardware.hw_unit_id and
                    hardware.hw_model_id = models.md_id AND hw_status.hwd_status_id = hardware.hw_status_id
                    AND models.md_brand_id = brands.br_id AND models.md_hardware_type = hw_type_id
                    ORDER BY  hw_type_order '''
        data_set = libpg.query_many(sql, (self.settings['unit_id'],))
        proc_html = report_lib.hardware_inventory_report(data_set, self.settings)
        form = report_display.DisplayReport(proc_html)
        form.exec_()

    def add_old_hw_click(self):
        form = hardware_edit.HardwareEdit({'hw_id': -1, 'hw_unit_id': self.settings['unit_id'], 'un_name': self.settings['un_name']})
        form.exec_()
        self.hw_status_change()

def main():
    app = QApplication(sys.argv)
    form = HardwareBrw({'model_id': 0, 'unit_id': 0})
    form.show()
    app.exec_()


if __name__ == '__main__':
    pass