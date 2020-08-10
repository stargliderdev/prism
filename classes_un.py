#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QLabel, QCheckBox, QVBoxLayout, QLineEdit, QTabWidget,QPushButton,\
     QWidget, QToolButton, QDateEdit, QTextEdit, QMessageBox, QCalendarWidget, QDesktopWidget,QTableWidget,QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import datetime
import uuid

import libpg
import parameters as gl
import qlib as qc
import liblogos
import ex_grid
import stdio
import unit_setup
import data_sets
import cp

class AddInteger(QDialog):
    def __init__(self, last_cnt, label, parent=None):
        super(AddInteger, self).__init__(parent)
        self.setWindowTitle(label[0])
        masterLayout = QVBoxLayout(self)
        self.current_int = QLineEdit()
        self.current_int.setReadOnly(True)
        self.current_int.setText('0')
        if last_cnt > -1:
            self.current_int.setText(str(last_cnt))
            masterLayout.addLayout(qc.addHLayout([label[1], self.current_int, True], lw=120))
        
        self.new_int = QLineEdit()
        self.new_int.setInputMask('DD')
        self.new_int.setText('3')
        
        masterLayout.addLayout(qc.addHLayout([label[2], self.new_int, True], lw=120))
        
        okBtn = QPushButton('Valida')
        # self.connect(okBtn, SIGNAL("clicked()"), self.save_click)
        okBtn.clicked.connect(self.save_click)
        
        cancelBtn = QPushButton('Cancela')
        # self.connect(cancelBtn, SIGNAL("clicked()"), self.cancel_btn_click)
        cancelBtn.clicked.connect(self.cancel_btn_click)
        
        masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
    
    def cancel_btn_click(self):
        self.ret = (False, '')
        self.close()
    
    def save_click(self):
        self.ret = (True, int(self.current_int.text()), int(self.new_int.text()))
        self.close()


class SetTextCommit(QDialog):
    def __init__(self, unit_id, cm_act_id, title,parent=None):
        super(SetTextCommit, self).__init__(parent)
        self.unit_id = unit_id
        self.cm_act_id = cm_act_id
        self.setWindowTitle(title)
        masterLayout = QVBoxLayout(self)
        self.text_1 = QLineEdit()
        masterLayout.addLayout(qc.addVLayout([kwargs['field1'], self.text_1, True]))
        okBtn = QPushButton('Valida')
        # self.connect(okBtn, SIGNAL("clicked()"), self.save_click)
        okBtn.clicked.connect(self.save_click)
        
        cancelBtn = QPushButton('Cancela')
        # self.connect(cancelBtn, SIGNAL("clicked()"), self.cancel_btn_click)
        cancelBtn.clicked.connect(self.cancel_btn_click)
        
        masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
    
    def cancel_btn_click(self):
        self.close()
    
    def save_click(self):
        liblogos.add_unit_comitment(self.unit_id, self.cm_act_id, self.text_1.text(), '', True)
        self.close()


class EditContact(QDialog):
    def __init__(self, ct_id, unit_id, title, v1, v2, way, parent=None):
        super(EditContact, self).__init__(parent)
        if way == 3: # horario
            l1 = 'Horário/Dia'
            l2 = 'Horário/Dia'
        else:
            l1 = 'Nome'
            l2 = 'Contacto'
        self.ret = False
        self.ct_id = ct_id
        self.unit_id = unit_id
        self.setWindowTitle(title)
        masterLayout = QVBoxLayout(self)
        self.text_1 = QLineEdit()
        self.text_2 = QLineEdit()
        # if way == 1 or way == 3:
        #     self.text_2.setInputMask('000000000')
        #     self.text_2.setMaxLength(9)
        # else:
        self.text_2.setMaxLength(100)
        self.text_2.setMinimumWidth(270)
        masterLayout.addLayout(qc.addHLayout([l1, self.text_1], lw=120))
        masterLayout.addLayout(qc.addHLayout([l2, self.text_2, True], lw=120))
        okBtn = QPushButton('Valida')
        okBtn.clicked.connect(self.save_click)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        
        masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
        if self.unit_id > -1:
            self.text_1.setText(v1)
            self.text_2.setText(v2)
    
    def cancel_btn_click(self):
        self.close()
    
    def save_click(self):
        if self.text_1.text() == '' or self.text_2.text() == '':
            pass
        else:
            liblogos.edit_unit_contacts(self.ct_id, self.text_1.text(), self.text_2.text())
            self.ret = True
            self.close()


class AddContactsBrowser(QDialog):
    def __init__(self, unit_id, parent=None):
        super(AddContactsBrowser, self).__init__(parent)
        self.ret = False
        masterLayout = QVBoxLayout(self)
        self.resize(300, 600)
        self.unit_id = unit_id
        self.setWindowTitle('Adicionar Contacto')
        self.contacts_grid = QTableWidget()
        self.contacts_grid.clicked.connect(self.add_contact_click)
        
        self.contacts_grid.setSelectionBehavior(QTableWidget.SelectRows)
        self.contacts_grid.setSelectionMode(QTableWidget.SingleSelection)
        self.contacts_grid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.contacts_grid.verticalHeader().setDefaultSectionSize(20)
        self.contacts_grid.setAlternatingRowColors(True)
        self.contacts_grid.setStyleSheet("alternate-background-color: #99ffcc;")
        self.contacts_grid.verticalHeader().setVisible(False)
        
        ex_grid.make_grid(self.contacts_grid, ['ct_id', 'Nome', 'multi', 'way'], [(0, 0), (1, 270), (2, 0), (3, 0)])
        masterLayout.addWidget(self.contacts_grid)
        hl = libpg.query_many('''SELECT ctt_id, ctt_name, ctt_multi, ctt_way
            FROM contact_types
            WHERE ctt_visible=True
              ORDER BY ctt_group, ctt_order''', (True,))
        ex_grid.grid_std(self.contacts_grid, data=hl, f_col=['i', 's', 'i', 'i'])
    
    def add_contact_click(self):
        # é um contacto novo claro, senão não vem aqui
        #      verifica se já existe um contacto deste tipo
        c = int(self.contacts_grid.item(self.contacts_grid.currentRow(), 0).text())
        bc = libpg.query_one('''SELECT ct_id FROM contacts WHERE contacts.ct_ctt_id = %s AND ct_unit = %s''', (c, self.unit_id))
        if bc is not None:
            if self.contacts_grid.item(self.contacts_grid.currentRow(), 2).text().strip() == 'True':
                a = liblogos.add_unit_contacts(c, self.unit_id)
                title = self.contacts_grid.item(self.contacts_grid.currentRow(), 1).text()
                way = int(self.contacts_grid.item(self.contacts_grid.currentRow(), 3).text())
                form = EditContact(a, self.unit_id, title, '', '', way)
                form.exec_()
            else:
                '''não pode adicionar'''
                QMessageBox.warning(None,"Contacto Duplicado","Este tipo de contacto \n não pode ser duplicado!\nTem de ser editada!")
        else:
            a = liblogos.add_unit_contacts(c, self.unit_id)
            title = self.contacts_grid.item(self.contacts_grid.currentRow(), 1).text()
            way = int(self.contacts_grid.item(self.contacts_grid.currentRow(), 3).text())
            form = EditContact(a, self.unit_id, title, '', '', way)
            form.exec_()
            if form.ret:
                self.ret = True
                self.close()


class TerminalsDialog(QDialog):
    def __init__(self, unit_id, setting_id, edit=False, names='', parent=None):
        super(TerminalsDialog, self).__init__(parent)
        self.edit = edit
        self.setting_id = setting_id
        self.unit_id = unit_id
        self.setWindowTitle('Alterar Postos')
        masterLayout = QVBoxLayout(self)
        
        self.new_terminals = QLineEdit()
        # self.new_terminals.setInputMask('DD')
        self.new_terminals.setText('2')
        self.terminal_names = QLineEdit()
        if edit:
            self.terminal_names.setText(names)
        masterLayout.addLayout(qc.addHLayout(['Novo # de Postos', self.new_terminals, True], lw=120))
        masterLayout.addLayout(qc.addHLayout(['Nomes dos Postos', self.terminal_names, True], lw=120))
        
        okBtn = QPushButton('Valida')
        okBtn.clicked.connect(self.save_click)
        
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        
        masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
    
    def cancel_btn_click(self):
        self.close()
    
    def save_click(self):
        if self.edit:
            liblogos.update_unit_settings(self.setting_id, int(self.new_terminals.text()), self.terminal_names.text())
        else:
            liblogos.insert_unit_setting(self.unit_id, self.setting_id, int(self.new_terminals.text()), self.terminal_names.text())
        self.close()


class InputDateComits(QDialog):
    def __init__(self, title, eternal=False, parent=None):
        super(InputDateComits, self).__init__(parent)
        self.ret = False, ''
        self.setWindowTitle(title)
        masterLayout = QVBoxLayout(self)
        self.calendar_QCalendarWidget = QCalendarWidget()
        masterLayout.addWidget(self.calendar_QCalendarWidget)
        lifetimeBtn = QPushButton('Vitalicio')
        lifetimeBtn.clicked.connect(self.lifetime_click)
        
        lifetimeBtn.setVisible(eternal)
        okBtn = QPushButton('Valida')
        okBtn.clicked.connect(self.save_click)
        
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        
        masterLayout.addLayout(qc.addHLayout([lifetimeBtn, okBtn, cancelBtn]))
    
    def cancel_btn_click(self):
        self.ret = False, ''
        self.close()
    
    def save_click(self):
        self.ret = True, self.calendar_QCalendarWidget.selectedDate().toPyDate().strftime('%Y-%m-%d')
        self.close()
    
    def lifetime_click(self):
        self.ret = (True,  datetime.datetime(2050, 1, 1).strftime('%Y-%m-%d'))
        # self.ret = (True, datetime.datetime(2050, 0o1, 0o1))
        self.close()


class InputDateSettings(QDialog):
    def __init__(self,setting_key, title, form_string, data=None, parent=None):
        super(InputDateSettings, self).__init__(parent)
        self.setWindowTitle(title)
        self.setting_key = setting_key
        self.data = data
        self.ret = (False,)
        masterLayout = QVBoxLayout(self)
        self.calendarQCalendarWidget = QCalendarWidget()
        self.calendarQCalendarWidget.setVerticalHeaderFormat(0)
        masterLayout.addWidget(self.calendarQCalendarWidget)
        lifetime_Btn = QPushButton('Vitalicio')
        lifetime_Btn.clicked.connect(self.lifetime_click)
        lifetime_Btn.setVisible(True)
        okBtn = QPushButton('Valida')
        okBtn.clicked.connect(self.save_click)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        masterLayout.addLayout(qc.addHLayout([lifetime_Btn, okBtn, cancelBtn]))
    
    def cancel_btn_click(self):
        self.ret = (False,)
        self.close()
    
    def save_click(self):
        if self.data is None:  
            print('insert')
            liblogos.insert_unit_setting(gl.unit_dict['un_id'], self.setting_key, self.calendarQCalendarWidget.selectedDate().toPyDate().strftime('%Y-%m-%d'), '')
        else:
            print('update')
            liblogos.update_unit_settings(self.setting_key, self.calendarQCalendarWidget.selectedDate().toPyDate().strftime('%Y-%m-%d'), '')
        self.ret = (True, self.calendarQCalendarWidget.selectedDate().toPyDate())
        self.close()
    
    def lifetime_click(self):
        if self.us_id == -1:
            liblogos.insert_unit_setting(gl.unit_dict['un_id'], self.setting_key, datetime.datetime(2050, 0o1, 0o1).strftime('%Y-%m-%d'))
        else:
            liblogos.update_unit_settings(self.setting_key, self.setting_key, datetime.datetime(2050, 0o1, 0o1).strftime('%Y-%m-%d'))
        self.ret = (True, datetime.datetime(2050, 0o1, 0o1).strftime('%Y-%m-%d'))
        self.close()


class InputInvoice(QDialog):
    def __init__(self, parent=None):
        super(InputInvoice, self).__init__(parent)
        self.setWindowTitle('Numero da Factura')
        masterLayout = QVBoxLayout(self)
        self.ret = (False, '')
        self.invoice = QLineEdit()
        self.invoice.setMaxLength(10)
        masterLayout.addLayout(qc.addHLayout(['Factura', self.invoice, True], lw=120))
        okBtn = QPushButton('Valida')
        okBtn.clicked.connect(self.save_click)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)

        masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
    
    def cancel_btn_click(self):
        self.close()
    
    def save_click(self):
        if self.invoice.text() == '':
            pass
        else:
            self.ret = (True, self.invoice.text())
        self.close()


class DbmsDialog(QDialog):
    def __init__(self, setting_key, title, data=None, parent=None):
        super(DbmsDialog, self).__init__(parent)
        self.setWindowTitle(title)
        masterLayout = QVBoxLayout(self)
        self.setting_key = setting_key
        self.data = data
        self.dbms_grd = QTableWidget()
        self.dbms_grd.setSelectionBehavior(QTableWidget.SelectRows)
        self.dbms_grd.setSelectionMode(QTableWidget.SingleSelection)
        self.dbms_grd.setEditTriggers(QTableWidget.NoEditTriggers)
        self.dbms_grd.verticalHeader().setDefaultSectionSize(20)
        self.dbms_grd.setAlternatingRowColors(True)
        self.dbms_grd.setStyleSheet("alternate-background-color: #89CFF0;")
        self.dbms_grd.verticalHeader().setVisible(False)
        self.dbms_grd.itemDoubleClicked.connect(self.save_click)
        ex_grid.make_grid(self.dbms_grd, ['Sistema e Versão'], [(0, 160)])
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        masterLayout.addLayout(qc.addHLayout([self.dbms_grd, True]))
        masterLayout.addLayout(qc.addHLayout([cancelBtn]))
        hl = libpg.sql_query('''SELECT db_edition from dbms
                where  db_active = True and substring(db_unit_type from ''' + str(
            gl.unit_dict['un_type']) + ''' for 1) = '1'  order by db_order ASC''')
        ex_grid.grid_std(self.dbms_grd, data=hl, f_col=['s'])
    
    def cancel_btn_click(self):
        self.close()
    
    def save_click(self):
        if self.data is None:
            liblogos.insert_unit_setting(gl.unit_dict['un_id'], 8, self.dbms_grd.item(self.dbms_grd.currentRow(), 0).text(), '')
        else:
            liblogos.update_unit_settings(self.setting_key, self.dbms_grd.item(self.dbms_grd.currentRow(), 0).text(), '')
        self.close()


class OsSetDialog(QDialog):
    def __init__(self, setting_key, title, form_string, data=None,parent=None):
        super(OsSetDialog, self).__init__(parent)
        self.setWindowTitle('Altera Sistema Operativo')
        masterLayout = QVBoxLayout(self)
        self.setting_key = setting_key
        self.title = title
        self.data = data
        self.os = QComboBox()
        self.os.setEditable(True)
        self.os.addItems(gl.os_version)
        self.os_arch = QComboBox()
        self.os_arch.setEditable(True)
        self.os_arch.addItems(['32 bit', '64 bit'])
        if self.data is None:
            pass
        else:
            self.os_arch.setEditText(data[1])
            self.os.setEditText(data[0])
        okBtn = QPushButton('Valida')
        okBtn.clicked.connect(self.save_click)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        masterLayout.addLayout(qc.addVLayout(['Sistema Operativo', self.os, 'Arquitectura', self.os_arch, True]))
        masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
    
    def cancel_btn_click(self):
        self.close()
    
    def save_click(self):
        if self.data is None:
            liblogos.insert_unit_setting(gl.unit_dict['un_id'], self.setting_key, self.os.currentText(), self.os_arch.currentText())
        else:
            liblogos.update_unit_settings(self.setting_key, self.os.currentText(), self.os_arch.currentText())
        self.close()


class ProductionPrinters(QDialog):
    def __init__(self, unit_id, setting_type, title, label_title, count=0,names='', edit=False, parent=None):
        super(ProductionPrinters, self).__init__(parent)
        # self.kwargs = kwargs
        self.edit = edit
        self.names = names
        self.count = count
        self.unit_id = unit_id
        self.setting_type = setting_type
        self.setWindowTitle(title)
        masterLayout = QVBoxLayout(self)
        self.rprinter_cnt = QLineEdit()
        # self.rprinter_cnt.setInputMask('DD')
        masterLayout.addLayout(qc.addHLayout(['Quantidade', self.rprinter_cnt, True], lw=180))
        self.rPrinterEdt = QLineEdit()
        self.rPrinterEdt.setMinimumWidth(200)
        masterLayout.addLayout(qc.addHLayout([label_title, self.rPrinterEdt, True], lw=180))
        
        okBtn = QPushButton('Valida')
        okBtn.clicked.connect(self.save_click)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        
        masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
        
        if self.edit == False:
            self.rprinter_cnt.setText('1')
        else:
            self.rprinter_cnt.setText(self.count)
            self.rPrinterEdt.setText(self.names)
    
    def cancel_btn_click(self):
        self.close()
    
    def save_click(self):
        """edita"""
        if self.edit:
            liblogos.update_unit_settings(self.us_id, self.rprinter_cnt.text(), self.rPrinterEdt.text())
        else:  # adiciona
            liblogos.insert_unit_setting(self.unit_id, self.setting_type, self.rprinter_cnt.text(), self.rPrinterEdt.text())
        self.close()


class InputTwoString(QDialog):
    """a setting key pode ser o tipo de setting se for novo ou o us_id se for para editar"""
    def __init__(self, setting_key, title, form_string, data=None, parent=None):
        super(InputTwoString, self).__init__(parent)
        self.resize(768, -1)
        form_string = form_string.split(';')
        self.setting_key = setting_key
        self.data = data
        self.setWindowTitle(title)
        masterLayout = QVBoxLayout(self)
        self.rprinter_cnt = QLineEdit()
        masterLayout.addLayout(qc.addHLayout([form_string[0], self.rprinter_cnt], lw=180))
        self.rPrinterEdt = QLineEdit()
        # self.rPrinterEdt.setMinimumWidth(200)
        masterLayout.addLayout(qc.addHLayout([form_string[1], self.rPrinterEdt], lw=180))
        okBtn = QPushButton('Valida')
        okBtn.clicked.connect(self.save_click)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
        
        if data is None:
            pass
        else:
            self.rprinter_cnt.setText(data[0])
            self.rPrinterEdt.setText(data[1])
    
    def cancel_btn_click(self):
        self.close()
    
    def save_click(self):
        """edita"""
        if self.data is None:
            """não tem dados so pode ser nova"""
            liblogos.insert_unit_setting(gl.unit_dict['un_id'], self.setting_key, self.rprinter_cnt.text(), self.rPrinterEdt.text())
        else:
            """tem dados edita"""
            liblogos.update_unit_settings(self.setting_key, self.rprinter_cnt.text(), self.rPrinterEdt.text())
        self.close()


class InputOneString(QDialog):
    """a setting key pode ser o tipo de setting se for novo ou o us_id se for para editar"""
    def __init__(self, setting_key, title, form_string, data=None, parent=None):
        super(InputOneString, self).__init__(parent)
        form_string = form_string.split(';')
        self.setting_key = setting_key
        self.data = data
        self.setWindowTitle(title)
        masterLayout = QVBoxLayout(self)
        self.rprinter_cnt = QLineEdit()
        masterLayout.addLayout(qc.addHLayout([form_string[0], self.rprinter_cnt, True], lw=180))
        okBtn = QPushButton('Valida')
        okBtn.clicked.connect(self.save_click)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
        
        if data is None:
            pass
        else:
            self.rprinter_cnt.setText(data[0])
    
    def cancel_btn_click(self):
        self.close()
    
    def save_click(self):
        """edita"""
        if self.data is None:
            """não tem dados so pode ser nova"""
            liblogos.insert_unit_setting(gl.unit_dict['un_id'], self.setting_key, self.rprinter_cnt.text(),'')
        else:
            """tem dados edita"""
            liblogos.update_unit_settings(self.setting_key, self.rprinter_cnt.text(), '')
        self.close()


# class SetISP(QDialog):
#     """a setting key pode ser o tipo de setting se for novo ou o us_id se for para editar"""
#     def __init__(self, setting_key, title, form_string, data=None, parent=None):
#         super(SetISP, self).__init__(parent)
#         form_string = form_string.split(';')
#         self.setting_key = setting_key
#         self.data = data
#         self.setWindowTitle('Fornecedor de Internet')
#         masterLayout = QVBoxLayout(self)
#         self.isp_b = QComboBox()
#         self.isp_b.setEditable(True)
#         self.isp_b.addItems(['Meo', 'Vodafone', 'Telepac', 'Nos', 'Cabovisão'])
#         self.isp_b.setEditText(form_string[0])
#         self.gateway_b = QLineEdit()
#         self.gateway_b.setText(form_string[1])
#         okBtn = QPushButton('Valida')
#         okBtn.clicked.connect(self.save_click)
#         cancelBtn = QPushButton('Cancela')
#         cancelBtn.clicked.connect(self.cancel_btn_click)
#         masterLayout.addLayout(qc.addVLayout(['Fornce. Internet ', self.isp_b, 'Gateway', self.gateway_b, True]))
#         masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
#
#         if data is None:
#             pass
#         else:
#             self.rprinter_cnt.setText(data[0])
#             self.rPrinterEdt.setText(data[1])
#
#     def cancel_btn_click(self):
#         self.close()
#
#     def save_click(self):
#         """edita"""
#         if self.data is None:
#             """não tem dados so pode ser nova"""
#             liblogos.insert_unit_setting(gl.unit_dict['un_id'], self.setting_key, self.isp_b.currentText(),
#                                          self.gateway_b.text())
#         else:
#             """tem dados edita"""
#             liblogos.update_unit_settings(self.setting_key, self.isp_b.text(), self.gateway_b.text())
#         self.close()
#
        

# class SetIsp(QDialog):
#     def __init__(self, parent=None, **kwargs):
#         super(SetIsp, self).__init__(parent)
#         self.setWindowTitle('Fornecedor de Internet')
#         masterLayout = QVBoxLayout(self)
#         self.kwargs = kwargs
#         self.isp_b = QComboBox()
#         self.isp_b.setEditable(True)
#         self.isp_b.addItems(['Meo', 'Vodafone', 'Telepac', 'Nos', 'Cabovisão'])
#         self.isp_b.setEditText(kwargs['v1'])
#         self.gateway_b = QLineEdit()
#         self.gateway_b.setText(kwargs['v2'])
#         okBtn = QPushButton('Valida')
#         okBtn.clicked.connect(self.save_click)
#         cancelBtn = QPushButton('Cancela')
#         cancelBtn.clicked.connect(self.cancel_btn_click)
#         masterLayout.addLayout(qc.addVLayout(['Fornce. Internet ', self.isp_b, 'Gateway', self.gateway_b, True]))
#         masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
#
#     def cancel_btn_click(self):
#         self.close()
#
#     def save_click(self):
#         if self.kwargs['edit']:
#             liblogos.update_unit_settings(self.kwargs['us_id'], self.isp_b.currentText(), self.gateway_b.text())
#         else:
#             liblogos.insert_unit_setting(self.kwargs['unit_id'], 12, self.isp_b.currentText(), self.gateway_b.text())
#         self.close()


class SetText(QDialog):
    def __init__(self, parent=None, **kwargs):
        super(SetText, self).__init__(parent)
        self.kwargs = kwargs
        self.setWindowTitle(kwargs['title'])
        masterLayout = QVBoxLayout(self)
        self.text_1 = QLineEdit()
        self.text_1.setMinimumWidth(300)
        masterLayout.addLayout(qc.addHLayout([kwargs['field1'], self.text_1, True], lw=180))
        self.text_2 = QLineEdit()
        self.text_2.setMinimumWidth(300)
        masterLayout.addLayout(qc.addHLayout([kwargs['field2'], self.text_2, True], lw=180))
        okBtn = QPushButton('Valida')
        okBtn.clicked.connect(self.save_click)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        
        masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
        if self.kwargs['edit']:
            self.text_1.setText(self.kwargs['v1'])
            self.text_2.setText(self.kwargs['v2'])
    
    def cancel_btn_click(self):
        self.close()
    
    def save_click(self):
        if self.kwargs['edit']:
            liblogos.update_unit_settings(self.kwargs['us_id'], self.text_1.text(), self.text_2.text())
        else:
            liblogos.insert_unit_setting(self.kwargs['unit_id'], self.kwargs['act_id'], self.text_1.text(),
                                         self.text_2.text())
        self.close()


class SetTextOne(QDialog):
    def __init__(self, parent=None, **kwargs):
        super(SetTextOne, self).__init__(parent)
        self.kwargs = kwargs
        self.setWindowTitle(kwargs['title'])
        masterLayout = QVBoxLayout(self)
        self.text_1 = QLineEdit()
        
        masterLayout.addLayout(qc.addHLayout([kwargs['field1'], self.text_1, True], lw=180))
        okBtn = QPushButton('Valida')
        okBtn.clicked.connect(self.save_click)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
        if self.kwargs['edit']:
            self.text_1.setText(self.kwargs['v1'])
    
    def cancel_btn_click(self):
        self.close()
    
    def save_click(self):
        if self.kwargs['edit']:
            liblogos.update_unit_settings(self.kwargs['us_id'], self.text_1.text(), '')
        else:
            liblogos.insert_unit_setting(self.kwargs['unit_id'], self.kwargs['act_id'], self.text_1.text(), '')
        self.close()


class SetArch(QDialog):
    def __init__(self, setting_key, title, form_string, data=None,parent=None):
        super(SetArch, self).__init__(parent)
        self.setWindowTitle('Arquitectura')
        masterLayout = QVBoxLayout(self)
        self.setting_key = setting_key
        self.title = title
        self.data = data
        self.arch = QComboBox()
        self.arch.setEditable(True)
        self.arch.addItems(['Servidor', 'Monoposto', 'Multiposto', 'Virtualizado', 'Cloud'])
        self.ip = QLineEdit()
        if self.data is None:
            pass
        else:
            self.arch.setEditText(data[0])
            self.ip.setText(data[1])
        okBtn = QPushButton('Valida')
        okBtn.clicked.connect(self.save_click)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        masterLayout.addLayout(qc.addVLayout(['Arquitectura', self.arch, 'IP Servidor', self.ip, True]))
        masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
    
    def cancel_btn_click(self):
        self.close()
    
    def save_click(self):
        if self.data is None:
            liblogos.insert_unit_setting(gl.unit_dict['un_id'], self.setting_key, self.arch.currentText(), self.ip.text())
        else:
            liblogos.update_unit_settings(self.setting_key, self.arch.currentText(), self.ip.text())
        self.close()


class UnitAdd(QDialog):
    def __init__(self, client_id, parent=None):
        super(UnitAdd, self).__init__(parent)
        self.resize(600, 400)
        self.setWindowTitle('Adiciona Unidade')
        bc = data_sets.get_unit_types()
        self.save_warning = False
        self.names = bc[0]
        self.u_dic = bc[1]
        mainLayout = QVBoxLayout(self)
        self.saveBtn = QPushButton('Grava')
        self.saveBtn.clicked.connect(self.save_click)
        self.cancelBtn = QPushButton('Cancela')
        self.cancelBtn.clicked.connect(self.exit_click)
        
        mainLayout.addLayout(qc.addHLayout([self.saveBtn, True, self.cancelBtn]))
        
        self.client_id = client_id
        self.un_id = QLineEdit()
        self.un_id.setFocusPolicy(Qt.NoFocus)
        self.un_id.setAlignment(Qt.AlignRight)
        self.un_id.setMinimumWidth(60)
        self.un_id.setMaximumWidth(60)
        self.un_id.setReadOnly(True)
        self.un_id.setStyleSheet("background-color: #dbf3ff;")
        self.un_id.setToolTip('Numero da Unidade')
        
        self.un_client_id = QLineEdit()
        self.un_client_id.setFocusPolicy(Qt.NoFocus)
        self.un_client_id.setAlignment(Qt.AlignRight)
        self.un_client_id.setMinimumWidth(60)
        self.un_client_id.setMaximumWidth(60)
        self.un_client_id.setReadOnly(True)
        self.un_client_id.setStyleSheet("background-color: #dbf3ff;")
        self.un_client_id.setToolTip('Numero do Cliente')
        
        self.un_client_name = QLineEdit()
        self.un_client_name.setFocusPolicy(Qt.NoFocus)
        self.un_client_name.setReadOnly(True)
        self.un_client_name.setStyleSheet("background-color: #dbf3ff;")
        self.un_client_name.setMinimumWidth(400)
        
        self.un_name = QLineEdit()
        self.un_name.setReadOnly(False)
        self.un_name.setStyleSheet("background-color: #ffffff;")
        self.un_name.setMinimumWidth(400)
        mainLayout.addLayout(qc.addHLayout(['Cliente:', self.un_client_name, True,
                                            self.un_client_id]))  # ,   self.change_cliente_Btn,'Conta:', self.un_conta_id,self.change_conta_Btn]))
        mainLayout.addLayout(qc.addHLayout(['Unidade:', self.un_name, True, self.un_id]))
        
        self.un_morada = QLineEdit()
        mainLayout.addLayout(qc.addHLayout(['Morada:', self.un_morada]))
        self.un_localidade = QLineEdit()
        self.un_localidade.setMaxLength(50)
        self.un_localidade.setObjectName('un_localidade')
        self.un_cp = QLineEdit()
        self.un_cp.setMaxLength(45)
        self.un_cp.setMaximumWidth(300)
        self.un_cp.setReadOnly(True)
        self.un_cp.setStyleSheet("background-color: #dbf3ff;")
        self.cp_drill_down = QToolButton()
        self.cp_drill_down.setIcon(QIcon('.//img//drill_down.png'))
        self.cp_drill_down.setToolTip('Procurar Código Postal')
        self.cp_drill_down.clicked.connect(self.cp_drill_down_click)
        
        mainLayout.addLayout(qc.addHLayout(['Localidade:', self.un_localidade]))
        mainLayout.addLayout(qc.addHLayout(['C.P.:', self.un_cp, self.cp_drill_down, True]))
        
        self.unit_type = QComboBox()
        self.unit_type.addItems(self.names)
        mainLayout.addLayout(qc.addHLayout(['Tipo:', self.unit_type, True]))
        mainLayout.addStretch()
        
        ''' refresh fields '''
        self.un_id.setText('????')
        cliente = libpg.query_one('SELECT cl_nome from clientes where cl_id = %s', (client_id,))
        self.un_client_name.setText(cliente[0].strip())
        self.un_client_id.setText(str(self.client_id))
    
    def cp_drill_down_click(self):
        self.save_warning = True
        form = cp.CpSearch()
        form.exec_()
        if form.ret[0]:
            self.un_morada.setText(form.ret[1])
            self.un_cp.setText(form.ret[2])
            self.un_localidade.setText(form.ret[3])
    
    def save_click(self):
        if self.validate_form()[0]:
            sql = '''INSERT into unidades (un_cliente_id, un_name,un_morada,un_localidade,un_cp, un_type, un_uuid)  VALUES(%s,%s,%s,%s,%s,%s,%s)'''
            data = (self.client_id, stdio.write_field(self.un_name), stdio.write_field(self.un_morada),
                    stdio.write_field(self.un_localidade),
                    stdio.write_field(self.un_cp).upper(), self.u_dic[str(self.unit_type.currentText())], str(uuid.uuid4()))
            libpg.execute_query(sql, data)
            unit = libpg.query_one('Select max(un_id) from unidades ')[0]
            self.close()
    
    def validate_form(self):
        b = (True, 'pass')
        if self.un_name.text() == '':
            b = (False, 'Sem Nome')
        elif self.un_morada.text() == '':
            b = (False, 'Sem Morada')
        elif self.un_localidade.text() == '':
            b = (False, 'Sem Localidade')
        elif self.un_cp.text() == '':
            b = (False, 'Sem Código Postal')
        if b[0] == False:
            QMessageBox.critical(None,"Erro de entrada de dados",b[1])
        return b
    
    def exit_click(self):
        if self.save_warning:
            res = QMessageBox.warning(None, self.tr("Aviso"),
                                      self.tr("""Foram efectuadas alterações! queres gravar?"""),
                                      QMessageBox.StandardButtons(
                                          QMessageBox.Cancel |
                                          QMessageBox.No |
                                          QMessageBox.Yes))
            if res == QMessageBox.Yes:
                self.save_click()
            elif res == QMessageBox.Cancel:
                pass
            else:
                self.close()
        else:
            self.close()


class OrderIws(QDialog):
    def __init__(self, parent=None, **kwargs):
        super(OrderIws, self).__init__(parent)
        self.unit_id = kwargs['unit_id']
        self.resize(600, 400)
        mainLayout = QVBoxLayout(self)
        self.setWindowTitle('Encomenda IWS')
        self.storage = QLineEdit()
        self.storage.setMaximumWidth(60)
        self.storage.setText('2.5 GB')
        self.storage.setReadOnly(True)
        self.storage.setStyleSheet("background-color: #dbf3ff;")
        self.storage_qtd = QLineEdit()
        self.storage_qtd.setText('1')
        self.storage_qtd.setMaximumWidth(60)
        self.connections = QLineEdit()
        self.connections.setMaximumWidth(60)
        self.connections.setText('1')
        self.dump_ok = QCheckBox('Dump Enviado')
        self.ass_id = QLineEdit()
        mainLayout.addLayout(qc.addHLayout(['Armazenamento:', self.storage, 'x', self.storage_qtd, True], lw=120))
        mainLayout.addLayout(qc.addHLayout(['Ligações:', self.connections, True], lw=120))
        mainLayout.addLayout(qc.addHLayout(['Assistencia #:', self.ass_id, self.dump_ok, True], lw=120))
        mainLayout.addStretch()
        self.saveBtn = QPushButton('Grava')
        self.saveBtn.clicked.connect(self.save_click)
        
        self.cancelBtn = QPushButton('Cancela')
        self.cancelBtn.clicked.connect(self.exit_click)
        
        mainLayout.addLayout(qc.addHLayout([self.saveBtn, True, self.cancelBtn]))
    
    def save_click(self):
        if self.validate_form()[0]:
            self.close()
    
    def validate_form(self):
        b = (False, 'pass')
        if self.ass_id.text() == '':
            b = (False, 'Sem Numero de Assistencia')
        else:
            if int(self.ass_id.text()) == False:
                b = (False, 'Assistencia não é um numero')
            else:
                if liblogos.scall_same_unit(self.unit_id, int(self.ass_id.text())) == False:
                    b = (False, 'A Assistencia não existe ou não é desta unidade')
                else:
                    b = (True, 'pass')
                    a = liblogos.get_unit_version(self.unit_id)
                    c = a.split('.')
                    if int(c[0]) < 2017:
                        b = (False, 'Versão inferior á 2017.')
                    else:
                        a = liblogos.get_dbms_version(self.unit_id)
                        c = a.split()
                        if float(c[1]) < 9.3:
                            b = (False, 'Versão do PostgreSQL não suportada.')
        if b[0] == False:
            QMessageBox.critical(None,"Erro na validação de dados",b[1])
        return b
    
    def exit_click(self):
        res = QMessageBox.warning(self, self.tr("Aviso"),
                                  self.tr("""Foram efectuadas alterações! queres sair?"""),
                                  QMessageBox.StandardButtons(
                                      QMessageBox.No |
                                      QMessageBox.Yes))
        if res == QMessageBox.Yes:
            self.close()
        else:
            self.save_click()


class DeactivetUnit(QDialog):
    def __init__(self, parent=None):
        super(DeactivetUnit, self).__init__(parent)
        self.setWindowTitle('Desactivar Unidade')
        masterLayout = QVBoxLayout(self)
        self.ret = (False,)
        self.reason = QComboBox()
        self.reason.setEditable(True)
        self.reason.addItems(['Fechou', 'Mudou de Dono', 'Mudou de Software'])
        okBtn = QPushButton('Confirma')
        okBtn.clicked.connect(self.save_click)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        
        masterLayout.addLayout(qc.addVLayout(['Motivo', self.reason, True]))
        masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
    
    def cancel_btn_click(self):
        self.close()
    
    def save_click(self):
        res = QMessageBox.warning(self, self.tr("Aviso"),
                                  self.tr("""Confirmas a desactivação da unidade?"""),
                                  QMessageBox.StandardButtons(
                                      QMessageBox.Yes |
                                      QMessageBox.Cancel))
        if res == QMessageBox.Yes:
            self.ret = (True, self.reason.currentText())
            self.close()
        elif res == QMessageBox.Cancel:
            self.ret = (False, 'pass')


if __name__ == '__main__':
    pass
