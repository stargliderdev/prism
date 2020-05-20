#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QLabel, QCheckBox, QVBoxLayout, QLineEdit, QAction,QTableWidget,QPushButton, QWidget,\
     QToolButton, QTabWidget, QTextEdit, QMessageBox, QFileDialog, QErrorMessage,QHBoxLayout, QInputDialog, QComboBox
from PyQt5.QtGui import QIcon,QPixmap, QFont
from PyQt5.Qt import Qt

import client_edit
import hardware
import hardware_edit
import msg_sms
import report_display
import smtpmail
import unit_comitments
import unit_transfer
import unit_type

try:
    import ctypes.wintypes
except:
    pass
import datetime
import json

import mod_eorder
import parameters as gl
import libpg
import data_sets
import stdio
import ex_grid
import os
import liblogos
import order_lic
import qlib as qc
import un_tags
import unit_files
import unit_setup
import classes_un
import cp
import uuid
import ftp_lic


class UnitEdit(QDialog):
    def __init__(self, unit_id, parent=None):
        super(UnitEdit, self).__init__(parent)
        self.resize(1024, 768)
        self.setWindowTitle('Ficha de Unidade')
        # vars
        gl.unit_dict = data_sets.unit_to_dic(unit_id)
        
        mainLayout = QVBoxLayout(self)
        self.saveBtn = QPushButton('Grava')
        self.saveBtn.clicked.connect(self.save_click)
        self.cancelBtn = QPushButton('Sair')
        self.cancelBtn.clicked.connect(self.exit_click)
        
        self.hamburguerMenuLabel = QLabel()
        pixmap = QPixmap('.//img//hamburger.png')
        self.hamburguerMenuLabel.setPixmap(pixmap)
        # menus do hamburger
        hw_in_unit = QAction("Equipamentos na Unidade", self)
        hw_in_unit.setIcon(QIcon('.//img//hwd_inventory.png'))
        hw_in_unit.triggered.connect(self.hardware_unit_process)
        self.hamburguerMenuLabel.addAction(hw_in_unit)
        hw_add_new = QAction("Adiciona Hardware Velho", self)
        hw_add_new.setIcon(QIcon('.//img//old_hardware.png'))
        hw_add_new.triggered.connect(self.add_old_hw_click)
        self.hamburguerMenuLabel.addAction(hw_add_new)
        addHardwareSerial = QAction("Adiciona Hardware por N/S", self)
        addHardwareSerial.setIcon(QIcon('.//img//old_hardware.png'))
        addHardwareSerial.triggered.connect(self.add_by_serial_number)
        self.hamburguerMenuLabel.addAction(addHardwareSerial)
        hw_add_new = QAction("Transfere Hardware", self)
        hw_add_new.setIcon(QIcon('.//img//move.png'))
        hw_add_new.triggered.connect(self.hardware_transfer_click)
        self.hamburguerMenuLabel.addAction(hw_add_new)
        sp1 = QAction(self)
        sp1.setSeparator(True)
        self.hamburguerMenuLabel.addAction(sp1)
        
        showUnitCodeAction = QAction("Código da Unidade", self)
        showUnitCodeAction.setIcon(QIcon('.//img//move.png'))
        showUnitCodeAction.triggered.connect(self.show_unit_code)
        self.hamburguerMenuLabel.addAction(showUnitCodeAction)
        deactivate = QAction("Desactivar Unidade", self)
        deactivate.setIcon(QIcon('.//img//deactivate.png'))
        deactivate.triggered.connect(self.deactivate_click)
        self.hamburguerMenuLabel.addAction(deactivate)
        
        self.hamburguerMenuLabel.setContextMenuPolicy(Qt.ActionsContextMenu)
        mainLayout.addLayout(qc.addHLayout([self.hamburguerMenuLabel, self.saveBtn, True, self.cancelBtn]))
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
        self.client_drill = QToolButton()
        self.client_drill.setIcon(QIcon('.//img//drill_down.png'))
        self.client_drill.setToolTip('Consultar Cliente')
        self.client_drill.clicked.connect(self.client_drill_down)
        
        self.un_nome = QLineEdit()
        self.un_nome.setFocusPolicy(Qt.NoFocus)
        self.un_nome.setReadOnly(True)
        self.un_nome.setStyleSheet("font-weight: bold; background-color: #dbf3ff;")
        self.un_nome.setMinimumWidth(400)
        
        self.un_uuid = QLineEdit()
        self.un_uuid.setFocusPolicy(Qt.NoFocus)
        self.un_uuid.setToolTip('uuid')
        self.un_uuid.setReadOnly(True)
        self.un_uuid.setAlignment(Qt.AlignCenter)
        self.un_uuid.setStyleSheet("background-color: #dbf3ff;")
        self.un_uuid.setMinimumWidth(300)
        
        self.cl_nif = QLineEdit()
        self.cl_nif.setFocusPolicy(Qt.NoFocus)
        self.cl_nif.setToolTip('NIF do Proprietário')
        self.cl_nif.setReadOnly(True)
        self.cl_nif.setAlignment(Qt.AlignCenter)
        self.cl_nif.setStyleSheet("background-color: #dbf3ff;")
        self.cl_nif.setMinimumWidth(80)
        
        self.cl_cc = QLineEdit()
        self.cl_cc.setFocusPolicy(Qt.NoFocus)
        self.cl_cc.setReadOnly(True)
        self.cl_cc.setAlignment(Qt.AlignRight)
        self.cl_cc.setStyleSheet("background-color: #dbf3ff;")
        self.cl_cc.setMinimumWidth(70)
        
        self.un_type = QLineEdit()
        self.un_type.setFocusPolicy(Qt.NoFocus)
        self.un_type.setReadOnly(True)
        self.un_type.setStyleSheet("background-color: #dbf3ff;")
        self.un_type.setMinimumWidth(50)
        unitTypeTBtn = QToolButton()
        unitTypeTBtn.setIcon(QIcon('.//img//drill_down.png'))
        unitTypeTBtn.setToolTip('Consultar Cliente')
        unitTypeTBtn.clicked.connect(self.unit_type_drill_down)
        self.un_activa = QCheckBox('Activa')
        
        mainLayout.addLayout(qc.addHLayout(['Unidade:', self.un_nome, 'Contribuite:', self.cl_nif, True, self.un_id]))
        mainLayout.addLayout(qc.addHLayout(['Cliente:', self.un_client_name, self.client_drill, True, 'Tipo:', self.un_type,unitTypeTBtn, 'C.C.', self.cl_cc, True, self.un_client_id]))
        
        self.un_morada = QLineEdit()
        self.un_localidade = QLineEdit()
        self.un_localidade.setMaxLength(50)
        self.un_localidade.setMaximumWidth(300)
        mainLayout.addLayout(qc.addHLayout(['Morada:', self.un_morada, 'Localidade:', self.un_localidade]))
        
        self.un_cp = QLineEdit()
        self.un_cp.setMaxLength(45)
        self.un_cp.setReadOnly(True)
        self.un_cp.setMinimumWidth(300)
        self.un_cp.setStyleSheet("background-color: #dbf3ff;")
        cp_drill = QToolButton()
        cp_drill.setIcon(QIcon('.//img//drill_down.png'))
        cp_drill.setToolTip('Consultar Cliente')
        cp_drill.clicked.connect(self.cp_drill_down)
        zoneDrillBt = QToolButton()
        zoneDrillBt.setIcon(QIcon('.//img//drill_down.png'))
        zoneDrillBt.setToolTip('Gerir Zonas')
        zoneDrillBt.clicked.connect(self.area_drill_down)

        self.zoneCBox = QComboBox()
        self.zoneCBox.setMinimumWidth(300)
        self.zoneCBox.addItems(gl.ds_areas)
        # self.zoneCBox.setEnabled(True)
        # self.zoneCBox.setEditable(True)
        mainLayout.addLayout(qc.addHLayout(['C.P.:', self.un_cp, cp_drill,True,self.zoneCBox, zoneDrillBt]))
        self.tabuladorTabWidget = QTabWidget()
        self.make_tab_settings()
        self.tabuladorTabWidget.addTab(self.tab1, 'Configurações')
        
        self.make_tab_contacts()
        self.tabuladorTabWidget.addTab(self.tab2, 'Contactos')
        self.make_tab_comits()
        self.tabuladorTabWidget.addTab(self.tab5, 'Compromissos')
        self.make_tab_memo_descrit()
        self.tabuladorTabWidget.addTab(self.tab4, 'Tags/Memoria Descritiva')
        
        if gl.unit_dict['un_type'] == 1:
            self.make_tab_restware_lic()
            self.tabuladorTabWidget.addTab(self.tab5, 'Licenças')
            self.make_tab_module_lic()
            self.tabuladorTabWidget.addTab(self.tab7, 'Modulos')
        mainLayout.addWidget(self.tabuladorTabWidget)
        if gl.unit_dict['un_id'] == -1:
            self.init_fields()
            self.un_id.setText('A atribuir')
            self.cliente_id = 0
            self.ct_id = 0
        else:
            self.update_fields()
            if not gl.unit_dict['un_activa']:
                self.saveBtn.setEnabled(False)
                self.add_tag.setEnabled(False)
    
    def unit_type_drill_down(self):
        form = unit_type.UnitTypeBrowser()
        form.exec_()
        if form.ret[0]:
            self.un_type.setText(form.ret[1])
            libpg.execute_query('update unidades set un_type = %s where un_id=%s', (form.ret[2],gl.unit_dict['un_id']))
            liblogos.log_actions(gl.user_dict, 'alter unit type ', 'unit_id ' + str(gl.unit_dict['un_id']) + ' to ' + str(form.ret[2]))
    
    def client_drill_down(self):
        form = client_edit.EditClient(gl.unit_dict['un_cliente_id'])
        form.exec_()
    
    def save_click(self):
        data = ()
        if gl.unit_dict['un_id'] > 0:
            sql = '''UPDATE unidades SET
                     un_nome=%s,un_morada=%s,un_localidade=%s,un_cp=%s, un_descricao=%s,
                     un_area= (select area_id from areas where lower(area_name) = %s)
                     WHERE un_id = %s '''
            data += (
                stdio.write_field(self.un_nome), stdio.write_field(self.un_morada),
                stdio.write_field(self.un_localidade),
                stdio.write_field(self.un_cp))
            data += (stdio.write_field(self.un_descricao),)
            data += (self.zoneCBox.currentText().lower(), gl.unit_dict['un_id'])
            libpg.execute_query(sql, data)
            if str(self.tags_stack) != str(self.un_tags_txt.toPlainText()):
                liblogos.update_unit_tags(gl.unit_dict['un_id'], self.un_tags_txt.toPlainText())
            self.close()
    
    def check_mandatory(self):
        toto = True
        if self.un_responsavel.text() == '':
            toto = False
        elif self.un_telefone.text() == '':
            toto = False
        return toto
    
    def activa_click(self):
        gl.unit_dict['un_activa'] = not gl.unit_dict['un_activa']
        if gl.unit_dict['un_activa']:
            self.un_activa.setText('Activa')
        else:
            self.un_activa.setText('Inactiva')
        update_activa = libpg.execute_query('UPDATE unidades set un_activa = %s where un_id=%s',(gl.unit_dict['un_activa'], gl.unit_dict['un_id']))
    
    def make_tab_contacts(self):
        # contactos
        self.tab2 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab2)
        tabLayout = QVBoxLayout()

        sendBtn = QPushButton('S.M.S')
        sendBtn.clicked.connect(self.send_sms_click)
        tabLayout.addLayout(qc.addHLayout([sendBtn,True]))
        self.contac_grid = QTableWidget()
        self.contac_grid.itemDoubleClicked.connect(self.contacts_grid_click)
        self.contac_grid.setSelectionBehavior(QTableWidget.SelectRows)
        self.contac_grid.setSelectionMode(QTableWidget.SingleSelection)
        self.contac_grid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.contac_grid.verticalHeader().setDefaultSectionSize(20)
        self.contac_grid.setAlternatingRowColors(True)
        self.contac_grid.setStyleSheet("alternate-background-color: #f5f5f0;")
        self.contac_grid.verticalHeader().setVisible(False)
        ex_grid.make_grid(self.contac_grid, ['ctt_id', 'unit','',  'Nome', 'Contacto','Tipo', 'tp'], [(0, 0), (1, 0), (2, 25), (3, 160), (4, 260), (5, 200),(6,0)])
        tabLayout.addWidget(self.contac_grid)
        mainTabLayout.addLayout(tabLayout)
        self.refresh_un_contacts()
        add_contact = QAction("Adiciona Contacto", self)
        add_contact.setIcon(QIcon('.//img//add2.png'))
        add_contact.triggered.connect(self.add_contact_click)
        
        self.contac_grid.addAction(add_contact)
        del_contact = QAction("Apaga Contacto", self)
        del_contact.setIcon(QIcon('.//img//delete2.png'))
        del_contact.triggered.connect(self.del_contact_click)
        
        self.contac_grid.addAction(del_contact)
        self.contac_grid.setContextMenuPolicy(Qt.ActionsContextMenu)
    
    def refresh_un_contacts(self):
        try:
            hl = libpg.query_many('''SELECT ct_id,ct_unit,(case when ctt_way =1 then '📲'
                when ctt_way =2 then '📧'
                when ctt_way =3 then '🕐'
                end) as way,   contacts.ct_value1, contacts.ct_value2,contact_types.ctt_name, contact_types.ctt_way
                FROM contacts
                  INNER JOIN contact_types ON (contacts.ct_ctt_id = contact_types.ctt_id)
                  where ct_unit =%s order by ctt_order,ctt_group ''', (gl.unit_dict['un_id'],))
            ex_grid.grid_std(self.contac_grid, data=hl, f_col=['i', 'i', 's','s', 's', 's', 'i'])
        except TypeError:
            pass
    
    def add_contact_click(self):
        form = classes_un.AddContactsBrowser(gl.unit_dict['un_id'])
        form.exec_()
        if form.ret:
            self.refresh_un_contacts()
    
    def del_contact_click(self):
        res = QMessageBox.warning(self, self.tr("Apagar"),
                                  self.tr("""Queres apagar este contacto?"""),
                                  QMessageBox.StandardButtons(
                                      QMessageBox.No |
                                      QMessageBox.Yes))
        if res == QMessageBox.Yes:
            ct_id = int(self.contac_grid.item(self.contac_grid.currentRow(), 0).text())
            libpg.execute_query('''delete from contacts where ct_id =%s''', (ct_id,))
            self.refresh_un_contacts()
    
    def contacts_grid_click(self):
        ct_id = int(self.contac_grid.item(self.contac_grid.currentRow(), 0).text())
        title = self.contac_grid.item(self.contac_grid.currentRow(), 5).text()
        v1 = self.contac_grid.item(self.contac_grid.currentRow(), 3).text()
        v2 = self.contac_grid.item(self.contac_grid.currentRow(), 4).text()
        way = int(self.contac_grid.item(self.contac_grid.currentRow(), 6).text())
        # unit_setup.edit_contact_main(ct_id, gl.unit_dict['un_id'], title, v1, v2, way)
        form = classes_un.EditContact(ct_id, gl.unit_dict['un_id'], title, v1, v2, way)
        form.exec_()
        if form.ret:
            self.refresh_un_contacts()
    
    def send_sms_click(self):
        form = msg_sms.MsgSendSMS(gl.unit_dict)
        form.exec_()
    
    def cp_drill_down(self):
        cp_list = self.un_cp.text().replace('-',' ')
        form = cp.CpSearch(cp_list.split())
        form.exec_()
        if form.ret[0]:
            if self.un_morada.text() == '':
                self.un_morada.setText(form.ret[1])
            self.un_cp.setText(form.ret[2])
            self.un_localidade.setText(form.ret[3])
    
    def area_drill_down(self):
        from area_manager import AreaManager
        form = AreaManager()
        form.exec_()
        ret = form.ret
        if ret['responce']:
            self.zoneCBox.clear()
            self.zoneCBox.addItems(gl.ds_areas)
            self.zoneCBox.setCurrentText(ret['area_name'])
        
    def make_tab_settings(self):
        # configurações"
        self.tab1 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab1)
        tabLayout = QVBoxLayout()
        self.un_sets = QTableWidget()
        self.un_sets.itemDoubleClicked.connect(self.edit_setting)
        self.un_sets.setSelectionBehavior(QTableWidget.SelectRows)
        self.un_sets.setSelectionMode(QTableWidget.SingleSelection)
        self.un_sets.setEditTriggers(QTableWidget.NoEditTriggers)
        self.un_sets.verticalHeader().setDefaultSectionSize(20)
        self.un_sets.setAlternatingRowColors(True)
        self.un_sets.setStyleSheet("alternate-background-color: #e6ffee;")
        self.un_sets.verticalHeader().setVisible(False)
        ex_grid.make_grid(self.un_sets, ['us_id', 'unit', 'Nome', 'Valor 1', 'Valor 2'],
                          [(0, 0), (1, 0), (2, 220), (3, 260), (4, 260)])
        tabLayout.addWidget(self.un_sets)
        mainTabLayout.addLayout(tabLayout)
        self.refresh_un_sets()
        self.tab1.setVisible(False)
        # context menu
        add = QAction("Adiciona Config", self)
        add.setIcon(QIcon('.//img//add2.png'))
        add.triggered.connect(self.add_setting)
        self.un_sets.addAction(add)
        delete = QAction("Apaga Config", self)
        delete.setIcon(QIcon('.//img//delete2.png'))
        delete.triggered.connect(self.del_setting_click)
        
        self.un_sets.addAction(delete)
        self.un_sets.setContextMenuPolicy(Qt.ActionsContextMenu)
    
    def refresh_un_sets(self):
        try:
            hl = libpg.query_many('''SELECT us_id, us_types.ust_id, us_types.ust_name, unit_settings.us_value1, unit_settings.us_value2
                FROM unit_settings
                  INNER JOIN us_types ON (unit_settings.us_act_id = us_types.ust_id)
                  where us_unit_id = %s order by ust_group,ust_order''', (gl.unit_dict['un_id'],))
            ex_grid.grid_std(self.un_sets, data=hl, f_col=['i', 'i', 's', 's', 's'])
        except TypeError:
            pass
        
    def add_setting(self):
        form = classes_un.AddSettingBrowser(gl.unit_dict['un_id'], gl.unit_dict['un_type'])
        form.exec_()
        self.refresh_un_sets()
    
    def edit_setting(self):
        us_id = int(self.un_sets.item(self.un_sets.currentRow(), 0).text())
        us_act_id = int(self.un_sets.item(self.un_sets.currentRow(), 1).text())
        v1 = self.un_sets.item(self.un_sets.currentRow(), 3).text()
        v2 = self.un_sets.item(self.un_sets.currentRow(), 4).text()
        unit_setup.edit_settings_main(us_id=us_id, act_id=us_act_id, unit_type=gl.unit_dict['un_type'],
                                      unit_id=gl.unit_dict['un_id'], v1=v1, v2=v2)
        self.refresh_un_sets()
    
    def del_setting_click(self):
        res = QMessageBox.warning(self, self.tr("Apagar"),
                                  self.tr("""Queres apagar esta Configuração?"""),
                                  QMessageBox.StandardButtons(QMessageBox.No | QMessageBox.Yes))
        if res == QMessageBox.Yes:
            c = int(self.un_sets.item(self.un_sets.currentRow(), 0).text())
            libpg.execute_query('''delete from unit_settings where us_id =%s''', (c,))
            self.refresh_un_sets()
    
    def make_tab_comits(self):
        # comprimissos do restware"
        self.tab5 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab5)
        tabLayout = QVBoxLayout()
        self.cmt_grd = QTableWidget()
        
        self.cmt_grd.setSelectionBehavior(QTableWidget.SelectRows)
        self.cmt_grd.setSelectionMode(QTableWidget.SingleSelection)
        self.cmt_grd.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cmt_grd.verticalHeader().setDefaultSectionSize(20)
        self.cmt_grd.setAlternatingRowColors(True)
        self.cmt_grd.setStyleSheet("alternate-background-color: #ffebe6;")
        self.cmt_grd.verticalHeader().setVisible(False)
        ex_grid.make_grid(self.cmt_grd, ['id', 'py', 'Descrição', 'Valor', 'Factura', 'Lançado'],
                          [(0, 0), (1, 0), (2, 260), (3, 100), (4, 160), (5, 200)])
        tabLayout.addWidget(self.cmt_grd)
        self.cmt_grd.itemDoubleClicked.connect(self.edit_comit)
        self.refresh_comitments()
        mainTabLayout.addLayout(tabLayout)
        
        add = QAction("Adiciona Compromisso", self)
        add.setIcon(QIcon('.//img//add2.png'))
        add.triggered.connect(self.add_comit)
        self.cmt_grd.addAction(add)
        delete_comit = QAction("Apaga Compromisso", self)
        delete_comit.setIcon(QIcon('.//img//delete2.png'))
        delete_comit.triggered.connect(self.del_comit)
        self.cmt_grd.addAction(delete_comit)
        log = QAction("Ver log", self)
        log.setIcon(QIcon('.//img//log.png'))
        log.triggered.connect(self.log_comit)
        
        self.cmt_grd.addAction(log)
        self.cmt_grd.setContextMenuPolicy(Qt.ActionsContextMenu)
    
    def refresh_comitments(self):
        try:
            hl = libpg.query_many(''' SELECT comitments_unit.cm_id,comitments_unit.cm_act_id, comit_types.cmt_name, comitments_unit.cm_value, comitments_unit.cm_invoice, cm_update
                FROM comitments_unit, comit_types
                WHERE comitments_unit.cm_unit_id=%s and comitments_unit.cm_act_id = comit_types.cmt_id and cm_archive = False
                ORDER BY comit_types.cmt_group ASC, comit_types.cmt_order ASC;''', (gl.unit_dict['un_id'],))
            ex_grid.grid_std(self.cmt_grd, data=hl, f_col=['i', 'i', 's', 's', 's', 't'])
        except TypeError:
            pass
    
    def add_comit(self):
        form = unit_comitments.AddCommitBrowser(gl.unit_dict['un_id'], gl.unit_dict['un_type'])
        form.exec_()
        self.refresh_comitments()
    
    def edit_comit(self):
        cmt_type = int(self.cmt_grd.item(self.cmt_grd.currentRow(), 1).text())
        is_edit = gl.commit_types[cmt_type][6]
        if is_edit == 1:
            unit_comitments.add_comitments_unit(gl.unit_dict['un_id'],cmt_type)
        else:
            QMessageBox.warning(None, "Erro","Este Compromisso não pode ser \nalterado daqui!")
        self.refresh_comitments()
    
    def del_comit(self):
        res = QMessageBox.warning(self, self.tr("Apagar"),
                                  self.tr("""Queres apagar este Compromisso?"""),
                                  QMessageBox.StandardButtons(
                                      QMessageBox.No |
                                      QMessageBox.Yes))
        if res == QMessageBox.Yes:
            ct_id = int(self.cmt_grd.item(self.cmt_grd.currentRow(), 0).text())
            libpg.execute_query('''delete from comitments_unit where cm_id =%s''', (ct_id,))
            self.refresh_comitments()
    
    def log_comit(self):
        hl = libpg.query_many(''' SELECT  comitments_unit.cm_id,comitments_unit.cm_act_id, comit_types.cmt_name, comitments_unit.cm_value,comitments_unit.cm_invoice,cm_update
            FROM comitments_unit, comit_types
            WHERE  comitments_unit.cm_unit_id=%s and comitments_unit.cm_act_id = comit_types.cmt_id and cm_archive = True
            ORDER BY  comit_types.cmt_group ASC,
              cm_update DESC;''', (gl.unit_dict['un_id'],))
        ex_grid.grid_std(self.cmt_grd, data=hl, f_col=['i', 'i', 's', 's', 's', 't'])
    
    def order_iws(self):
        pass
    
    def refresh_cmt_restware(self):
        hl = libpg.query_many(''' SELECT comitments_unit.cm_id,comitments_unit.cm_act_id, comit_types.cmt_name, comitments_unit.cm_value, comitments_unit.cm_invoice, cm_update
            FROM comitments_unit, comit_types
            WHERE comitments_unit.cm_unit_id=%s and comitments_unit.cm_act_id = comit_types.cmt_id and cm_archive = False
            ORDER BY comit_types.cmt_group ASC, comit_types.cmt_order ASC;''', (gl.unit_dict['un_id'],))
        ex_grid.grid_std(self.cmt_grd, data=hl, f_col=['i', 'i', 's', 's', 's', 't'])
    
    def add_cmt_restware(self):
        if gl.unit_dict['un_conta_id'] > 0:
            # tem conta: não pode lançar compromisso pela unidade
            QMessageBox.warning(None, "Erro","Esta <b>Unidade</b> tem uma <b>Conta</b>\n e este <b>Compromisso</b> não pode ser \nalterado daqui!")
        else:
            form = unit_setup.AddCommitBrowser(gl.unit_dict['un_id'])
            form.exec_()
        self.refresh_comitments()
    
    def edit_cmt_restware(self):
        cmt_type = int(self.cmt_restware_grd.item(self.cmt_restware_grd.currentRow(), 1).text())
        is_edit = gl.commit_types[cmt_type][7]
        if is_edit == 1:
            # unit_setup.edit_unit_comitments(cmt_type, gl.unit_dict['un_id'])
            pass
        else:
            QMessageBox.warning(None,"Erro","Este  <b>Compromisso</b> não pode ser \nalterado daqui!")
        self.refresh_cmt_restware()
    
    def log_cmt_restware(self):
        hl = libpg.query_many(''' SELECT
              comitments_unit.cm_id,comitments_unit.cm_act_id, comit_types.cmt_name, comitments_unit.cm_value,comitments_unit.cm_invoice,cm_update
            FROM
              comitments_unit, comit_types
            WHERE
              comitments_unit.cm_unit_id=%s and comitments_unit.cm_act_id = comit_types.cmt_id and cm_archive = True
            ORDER BY
              comit_types.cmt_group ASC,
              cm_update DESC;''', (gl.unit_dict['un_id'],))
        ex_grid.grid_std(self.cmt_restware_grd, data=hl, f_col=['i', 'i', 's', 's', 's', 't'])
    
    def make_tab_memo_descrit(self):
        self.save_warning = False
        self.tab4 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab4)
        self.add_tag = QToolButton()
        self.add_tag.setIcon(QIcon('.//img//add2.png'))
        # self.connect(self.add_tag, SIGNAL("clicked()"), self.add_tags_click)
        self.add_tag.clicked.connect(self.add_tags_click)
        
        mainTabLayout.addLayout(qc.addHLayout([self.add_tag, True]))
        self.un_tags_txt = QTextEdit()
        self.un_tags_txt.setMaximumHeight(100)
        self.un_descricao = QTextEdit()
        font = QFont()
        font.setFamily("Monospace")
        font.setWeight(50)
        self.un_descricao.setFont(font)
        mainTabLayout.addLayout(qc.addVLayout([self.un_tags_txt, self.un_descricao]))
    
    def make_tab_files(self):
        # ficheiros
        self.tab6 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab6)
        tabLayout = QVBoxLayout()
        self.files_grd = QTableWidget()
        self.files_grd.itemDoubleClicked.connect(self.edit_comit)
        
        self.files_grd.setSelectionBehavior(QTableWidget.SelectRows)
        self.files_grd.setSelectionMode(QTableWidget.SingleSelection)
        self.files_grd.setEditTriggers(QTableWidget.NoEditTriggers)
        self.files_grd.verticalHeader().setDefaultSectionSize(20)
        self.files_grd.setAlternatingRowColors(True)
        self.files_grd.setStyleSheet("alternate-background-color: lightblue;")
        self.files_grd.verticalHeader().setVisible(False)
        ex_grid.make_grid(self.files_grd, ['uuid', 'Tipos', 'Descrição', 'Data', 'Quem', '.ext', 'Quando'],
                          [(0, 0), (1, 140), (2, 400), (3, 90), (4, 90), (5, 70), (6, 130)])
        tabLayout.addWidget(self.files_grd)
        mainTabLayout.addLayout(tabLayout)
        add = QAction("Adiciona Ficheiro", self)
        add.setIcon(QIcon('.//img//add2.png'))
        add.triggered.connect(self.file_add)
        self.files_grd.addAction(add)
        log = QAction("Download ficheiro", self)
        log.setIcon(QIcon('.//img//log.png'))
        log.triggered.connect(self.file_download)
        self.files_grd.addAction(log)
        self.files_grd.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.refresh_files_att()
    
    def refresh_files_att(self):
        hl = libpg.query_many('''SELECT un_fref_uuid, un_ftype_name, un_fref_des, to_char(un_fref_data,'dd-MM-YYYY'), un_fref_who, un_fref_ext,
              to_char(un_fref_tstamp,'dd-MM-YYYY HH24:MI')un_fref_tstamp
              from unit_files_ref, unit_files_types
              where un_fref_unit=%s and un_fref_show=True
              and un_fref_ftype= un_ftype_id
              order by un_fref_tstamp desc ''', (gl.unit_dict['un_id'],))
        ex_grid.grid_std(self.files_grd, data=hl, f_col=['s', 's', 's', 's', 's', 's', 's'])
    
    def file_add(self):
        form = unit_files.AddUnitFile(gl.unit_dict['un_id'], gl.unit_dict['cl_nif'])
        form.exec_()
        self.refresh_files_att()
    
    def file_download(self):
        b = str(self.files_grd.item(self.files_grd.currentRow(), 0).text())
        f_name = libpg.query_one('select un_fref_fname, un_fref_ext from unit_files_ref where un_fref_uuid=%s', (b,))
        res = QFileDialog.getSaveFileName(
            None,
            self.tr("Guarda Ficheiro Como..."),
            self.tr(gl.unit_file_path + f_name[0]),
            self.tr("*." + f_name[1]))
        if not res == '':
            libpg.read_unit_bin(res, b)
            path_name, file_name = os.path.split(str(res))
            gl.unit_file_path = str(path_name + '\\')
    
    def add_tags_click(self):
        self.save_warning = True
        form = un_tags.UnitTagsBrowser()
        form.exec_()
        if form.tag_list[0] == 0:
            self.un_tags_txt.setPlainText(form.tag_list[1])
        elif form.tag_list[0] == 1:
            self.un_tags_txt.setPlainText(self.un_tags_txt.toPlainText() + ',' + form.tag_list[1])
    
    def make_tab_restware_lic(self):
        self.tab5 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab5)
        btn_layout = QHBoxLayout()
        refreshBtn = QPushButton('Actualiza')
        refreshBtn.clicked.connect(self.refresh_sf_click)
        self.new_licBtn = QPushButton('Nova')
        self.new_licBtn.setEnabled(False)
        self.new_licBtn.clicked.connect(self.new_lic_click)
        self.renew_licBtn = QPushButton('Re-Nova')
        self.renew_licBtn.setEnabled(False)
        self.renew_licBtn.clicked.connect(self.renew_lic_click)
        self.active_licBtn = QPushButton('Activar')
        self.active_licBtn.setEnabled(False)
        self.active_licBtn.clicked.connect(self.active_lic_click)
        self.upload_licBtn = QPushButton('Upload')
        self.upload_licBtn.setEnabled(True)
        self.upload_licBtn.clicked.connect(self.upload_lic_click)
        btn_layout.addLayout(qc.addHLayout([refreshBtn, True, self.new_licBtn, self.renew_licBtn,self.active_licBtn,self.upload_licBtn, True]))
        mainTabLayout.addLayout(btn_layout)
        self.softwareGrid = QTableWidget(self)
        self.softwareGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.softwareGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.softwareGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.softwareGrid.verticalHeader().setDefaultSectionSize(20)
        self.softwareGrid.setAlternatingRowColors(True)
        self.softwareGrid.verticalHeader().setVisible(False)
        self.softwareGrid.setStyleSheet("alternate-background-color: #e6e6ff;")
        self.softwareGrid.itemDoubleClicked.connect(self.show_lic_click)
        mainTabLayout.addWidget(self.softwareGrid)
        ex_grid.make_grid(self.softwareGrid, ['ID', 'Situação', 'Quem', 'Validade', 'Tipo Lic.', 'Quando', 'Estado', 'status'],
                          [(0, 60), (1, 130), (2, 100), (3, 100), (4,100),(5,130),(6,100), (7,0)])
        self.tab5.setVisible(False)
    
    def refresh_sf_click(self):
        if gl.unit_dict['un_activa']:
            self.new_licBtn.setEnabled(True)
            self.renew_licBtn.setEnabled(True)
            self.active_licBtn.setEnabled(True)
        sql = '''SELECT  software.sf_id,
                 lic_st_name,sf_who,
                 to_char(software.sf_date_valid, 'YYYY-MM-DD') as ds,software.sf_lic_type,
                 to_char(software.sf_time_order, 'YYYY-MM-DD HH24:MI') as dord,(case when software.sf_active = True then 'Activo '
                 else 'Inactivo' end) as status, lic_st_id
                 FROM software, software_type,software_lic_status
                 WHERE software.sf_unit_id = %s and software.sf_version = software_type.sft_id and
                       sf_status=lic_st_id
                 ORDER BY software.sf_id DESC, sf_date_valid DESC;'''
        hl = libpg.query_many(sql, (gl.unit_dict['un_id'],))
        ex_grid.grid_std(self.softwareGrid, data=hl, f_col=['i', 's', 's', 's', 's', 's', 's','i'])
    
    def show_lic_click(self):
        ld = data_sets.licence_to_dict(int(self.softwareGrid.item(self.softwareGrid.currentRow(), 0).text()))
        lic_json = json.loads(ld[6])['0']
        toto = liblogos.lic_view(lic_json, 'Licença')
        form = report_display.DisplayReport(toto)
        form.exec_()
    
    def new_lic_click(self):
        form = order_lic.MakeLic(gl.unit_dict['un_id'], -1)
        form.exec_()
    
    def renew_lic_click(self):
        try:
            # 0 e um renovação
            form = order_lic.MakeLic(gl.unit_dict['un_id'], 0)
            form.exec_()
        except AttributeError:
            pass
    
    def active_lic_click(self):
        try:
            """  activa a licença transferindo os dados para os commitments e settings
            mas só se estiver com status 3: em actualização
            """
            if int(self.softwareGrid.item(self.softwareGrid.currentRow(), 7).text()) in (3,5):
                lic_id = int(self.softwareGrid.item(self.softwareGrid.currentRow(), 0).text())
                """ verifica se é a ultima licença gerada, se não for não activa """
                bc = libpg.query_one('SELECT max(sf_id) as a from software where sf_unit_id=%s', (gl.unit_dict['un_id'],))[0]
                if bc == lic_id:
                    ''' activa lic e marca como atualizada'''
                    libpg.execute_query('''UPDATE software set sf_active = %s where sf_unit_id = %s''', (False, gl.unit_dict['un_id']))
                    libpg.execute_query('''UPDATE software set sf_active = %s, sf_status = 1 where sf_id = %s''', (False, lic_id))
                    ''' cria uma copia que essa é que fica activa'''
                    # lic_id = libpg.query_one(sql, (unit_id,))[0]
                    sql = '''INSERT INTO software (sf_unit_id, sf_lic_json, sf_version, sf_date_contract,
                                        sf_date_valid, sf_lic_type,sf_json_version, sf_status, sf_who, sf_active)
                                        SELECT sf_unit_id, sf_lic_json, sf_version, sf_date_contract,
                                        sf_date_valid, sf_lic_type,sf_json_version, 4, %s, True
                                        FROM software where sf_id= %s'''
                    data = (gl.user_dict['user_name'], lic_id)
                    libpg.execute_query(sql, data)
                    ''' lế a licença e actualiza os commits '''
                    a = data_sets.licence_to_dict(lic_id)
                    ''''carrega dicionario com os dados da licenca da base de dados'''
                    lic_dict = json.loads(a[6])['0']
                    liblogos.set_unit_comitments(gl.unit_dict['un_id'], 1, lic_dict['software'])
                    try:
                        lic_dict['terminals'] = lic_dict['units']
                    except KeyError:
                        lic_dict['terminals'] = '1'
                    liblogos.set_unit_comitments(gl.unit_dict['un_id'], 2, lic_dict['terminals'])
                    lic_dict['version'] = lic_dict.get('version',gl.PRODUCTION_VERSION)
                    lic_dict['terminals'] = lic_dict.get('terminals','1')
                    try:
                        lic_dict['clockin'] = lic_dict['clockin']
                    except KeyError:
                        lic_dict['clockin'] = '1'
                    liblogos.set_unit_comitments(gl.unit_dict['un_id'], 6, lic_dict['clockin'])
                    liblogos.set_unit_comitments(gl.unit_dict['un_id'], 14, lic_dict['date_valid'])
                    liblogos.set_unit_comitments(gl.unit_dict['un_id'], 13, lic_dict['date_valid'])
                    liblogos.set_unit_comitments(gl.unit_dict['un_id'], 12, lic_dict['date_contract'])
                    ''' update settings '''
                    liblogos.set_unit_settings(gl.unit_dict['un_id'], 1, lic_dict['software'], lic_dict['version'])
                    if lic_dict['terminals'] == '':
                        lic_dict['terminals'] = '1'
                    liblogos.set_unit_settings(gl.unit_dict['un_id'], 2, lic_dict['terminals'])
                    liblogos.set_unit_settings(gl.unit_dict['un_id'], 26, datetime.datetime.now().strftime("%Y-%m-%d"), gl.user_dict['user_name'])
                    liblogos.set_unit_settings(gl.unit_dict['un_id'], 28, lic_dict['commercial_version'], '')
                    try:
                        liblogos.set_unit_settings(gl.unit_dict['un_id'], 7, lic_dict['rdp'], '')
                    except KeyError:
                        libpg.execute_query('delete from unit_settings where us_unit_id = %s and us_act_id=%s', (gl.unit_dict['un_id'], 7))
                    try:
                        liblogos.set_unit_settings(gl.unit_dict['un_id'], 29, lic_dict['printon'], '')
                    except KeyError:
                        libpg.execute_query('delete from unit_settings where us_unit_id = %s and us_act_id=%s', (gl.unit_dict['un_id'], 29))
                        
                    '''actualiza as grelhas'''
                    self.refresh_cmt_restware()
                    self.refresh_un_sets()
                    self.refresh_sf_click()
                else:
                    QMessageBox.warning(None, "Erro",'Não foi a ultima licença gerada.\nLicença não activada')
            else:
                QMessageBox.warning(None, "Erro",
                                    "Esta licença não pode ser activada!")
        except Exception as e:
            errorMessage = QErrorMessage(self)
            errorMessage.showMessage('Ocorreu um erro:' + str(e))
    
    def upload_lic_click(self):
        """ :return: faz umas chamadas ao windows """
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value
        try:
            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
            local_path = buf.value + '\\2020.1'
        except NameError:
            local_path = '/home/zorze/tmp/Arlindo'
        fname = QFileDialog.getOpenFileName(self, 'Open file',local_path,'*.rar')[0]
        if not fname == '':
            check_nif = fname.find(gl.unit_dict['cl_nif'])
            if check_nif > -1:
                r = ftp_lic.send_lic_ftp(fname)
                if r[0]:
                    lic_number = liblogos.order_mark_upload(gl.unit_dict['un_id'])
                    if lic_number == -1:
                        QMessageBox.information(None, 'Upload da Licença', 'Licença re-carregada!')
                    else:
                        smtpmail.upload_lic_mail(lic_number, gl.unit_dict)
                        QMessageBox.information(None, 'Upload da Licença', 'Licença carregada com sucesso!')
                        self.refresh_sf_click()
                else:
                    QMessageBox.information(None, 'Erro', 'Licença com  Nome\n' + fname + ' gerou um erro: ' + r[1])
            else:
                QMessageBox.warning(None, 'Erro', 'A Licença não pertence a este cliente/unidade!')

    
    def make_tab_module_lic(self):
        self.tab7 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab7)
        btn_layout = QHBoxLayout()
        
        self.newBtn = QPushButton('eOrder')
        self.newBtn.setEnabled(True)
        self.newBtn.clicked.connect(self.add_eorder_click)
        self.refreshBtn = QPushButton('Atualiza')
        self.refreshBtn.clicked.connect(self.refresh_eorder_click)
        btn_layout.addLayout(qc.addHLayout([self.newBtn,self.refreshBtn, True]))
        mainTabLayout.addLayout(btn_layout)
        
        self.modulesGrid = QTableWidget(self)
        self.modulesGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.modulesGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.modulesGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.modulesGrid.verticalHeader().setDefaultSectionSize(20)
        self.modulesGrid.setAlternatingRowColors(True)
        self.modulesGrid.verticalHeader().setVisible(False)
        self.modulesGrid.itemDoubleClicked.connect(self.show_module_click)
        
        mainTabLayout.addWidget(self.modulesGrid)
        ex_grid.make_grid(self.modulesGrid, ['ID', 'Data de Fim'],[(0, 60), (1, 200)])
        self.tab7.setVisible(False)
    
    def show_module_click(self):
        ld = data_sets.eorder_to_dict(int(self.modulesGrid.item(self.modulesGrid.currentRow(), 0).text()))
        eorder_json = json.loads(ld[0])['0']
        toto = liblogos.eorder_to_html(eorder_json, 'Consulta de eOrder')
        form = report_display.DisplayReport(toto)
        form.exec_()
    
    def add_eorder_click(self):
        form = mod_eorder.MakeEorder(gl.unit_dict['un_id'])
        form.exec_()
    
    def refresh_eorder_click(self):
        sql = '''SELECT  mo_id, to_char(mo_date_valid,'YYYY-MM-DD') as dt
                    FROM modules where  mo_unit_id = %s  ORDER BY mo_id DESC'''
        hl = libpg.query_many(sql, (gl.unit_dict['un_id'],))
        ex_grid.grid_std(self.modulesGrid, data=hl, f_col=['i', 's'])
    
    def init_fields(self):
        self.un_id.clear()
        self.un_nome.clear()
        self.un_morada.clear()
        self.un_localidade.clear()
        self.un_cp.clear()
        self.un_postos.setValue(1)
        self.un_telefone.clear()
        self.un_movel.clear()
        self.un_responsavel.clear()
        self.un_servidor.setCheckState(Qt.Unchecked)
        self.un_servidor_ip.setText('0.0.0.0')
        self.un_imp_contas.setValue(1)
        self.un_imp_producao.setValue(0)
        self.un_mon_pedidos.setValue(0)
        self.un_sessoes_rdp.setValue(0)
        self.un_teamviewer_id.clear()
        self.un_horario.clear()
        self.un_ddns.clear()
        self.un_descricao.clear()
        self.un_contactos.clear()
        self.un_uuid.setText(str(uuid.uuid4()))
    
    def update_fields(self):
        stdio.read_field(self.un_id, 'un_id', gl.unit_dict)
        stdio.read_field(self.un_nome, 'un_nome', gl.unit_dict)
        stdio.read_field(self.un_type, 'un_type_name', gl.unit_dict)
        stdio.read_field(self.un_morada, 'un_morada', gl.unit_dict)
        stdio.read_field(self.un_localidade, 'un_localidade', gl.unit_dict)
        stdio.read_field(self.un_cp, 'un_cp', gl.unit_dict)
        stdio.read_field(self.un_descricao, 'un_descricao', gl.unit_dict)
        stdio.read_field(self.un_uuid, 'un_uuid', gl.unit_dict)
        stdio.read_field(self.cl_nif, 'cl_nif', gl.unit_dict)
        stdio.read_field(self.cl_cc, 'cl_cc', gl.unit_dict)
        cliente = libpg.query_one('SELECT cl_nome from clientes where cl_id = %s',  (gl.unit_dict['un_cliente_id'],))
        self.un_client_name.setText(cliente[0].strip())
        self.un_client_id.setText(str(gl.unit_dict['un_cliente_id']))
        self.zoneCBox.setCurrentText(gl.unit_dict['area_name'])
        self.tags_stack = self.get_tags()
        self.un_tags_txt.setPlainText(self.tags_stack)
    
    def get_tags(self):
        sql = '''SELECT tags_unit.tau_name FROM tag_un_refs, tags_unit WHERE
                tag_un_refs.tau_tag_id = tags_unit.tau_id and tag_unit_id=%s;'''
        a = libpg.query_many(sql, (gl.unit_dict['un_id'],))
        tags = ''
        for n in a:
            tags += n[0].lower() + ','
        return tags.rstrip(',')
    
    def hardware_transfer_click(self):
        form = unit_transfer.UnitTransfer()
        form.exec_()
    
    def add_old_hw_click(self):
        form = hardware_edit.HardwareEdit({'hw_id': -1, 'hw_unit_id': gl.unit_dict['un_id'], 'un_nome': gl.unit_dict['un_nome']})
        form.exec_()
    
    def add_by_serial_number(self):
        b, ok = QInputDialog.getText(self, "Adiciona por N/S", "Numero de Série:", QLineEdit.Normal)
        if ok and not b == '':
            hardware_id = libpg.query_one('select hw_id from hardware where upper(hw_sn)=%s', (b.upper(),))
            if hardware_id is None:
                QMessageBox.critical(None, 'Erro', "O numero de Serie " + b + ' não existe!')
            else:
                libpg.execute_query('update hardware set hw_unit_id=%s where hw_id=%s',(gl.unit_dict['un_id'], hardware_id))
                QMessageBox.information(None, 'Sucesso', 'Hardware transferido com sucesso!')
        else:
            pass
    
    def deactivate_click(self):
        if not gl.unit_dict['un_activa']:
            QMessageBox.critical(None, "Erro", "Unidade já desactivada")
        else:
            form = classes_un.DeactivetUnit()
            form.exec_()
            if form.ret[0]:
                self.un_tags_txt.setText(self.un_tags_txt.toPlainText() + ',' + form.ret[1])
                self.un_nome.setText(self.un_nome.text() + datetime.datetime.now().strftime(" [%Y-%m-%d]"))
                libpg.execute_query('update unidades set un_activa=%s where un_id=%s', (False, gl.unit_dict['un_id']))
                libpg.execute_query('update assistencias set proc_pendente=%s where proc_unit_id=%s', (False, gl.unit_dict['un_id']))
                libpg.execute_query('INSERT INTO unit_settings (us_unit_id, us_act_id, us_value1, us_value2) '
                                    'VALUES (%s, 24, %s, %s )', (gl.unit_dict['un_id'], datetime.datetime.now().strftime("%Y-%m-%d"),form.ret[1]))
                self.save_click()
    
    def get_software_as_text(self):
        sft = libpg.query_one('select sft_software from software_type where sft_id=%s', (gl.unit_dict['un_software'],))[0]
        self.software_txt.setText(sft + ' ' + gl.unit_dict['un_software_version'])
    
    def show_unit_code(self):
        a = gl.unit_dict['un_id']
        a = format(a, '04x')
        # 25+10+hex(un_id)
        hl = (gl.unit_dict['un_uuid'][25:26] + gl.unit_dict['un_uuid'][10:11] + "-" + a).upper()
        QMessageBox.information(None, "Código de unidade", hl)
    
    def hardware_unit_process(self):
        form = hardware.HardwareBrw({'unit_id': gl.unit_dict['un_id'], 'model_id': 0, 'un_nome': gl.unit_dict['un_nome']})
        form.exec_()
    
    def setBtnSizes(self, object, value=60):
        object.setMaximumHeight(value)
        object.setMinimumHeight(value)
        object.setMaximumWidth(value)
        object.setMinimumWidth(value)
    
    def setSize(self, obj, a, l):
        obj.setMaximumHeight(a)
        obj.setMinimumHeight(a)
        obj.setMaximumWidth(l)
        obj.setMinimumWidth(l)
    
    def setSizeWidth(self, object, value):
        object.setMaximumWidth(value)
        object.setMinimumWidth(value)
    
    def exit_click(self):
        if self.save_warning:
            res = QMessageBox.warning(self, self.tr("Aviso"),
                                      self.tr("""Foram efectuadas alterações! queres gravar?"""),
                                      QMessageBox.StandardButtons(QMessageBox.Cancel | QMessageBox.No | QMessageBox.Yes))
            if res == QMessageBox.Yes:
                self.save_click()
            elif res == QMessageBox.Cancel:
                pass
            else:
                self.close()
        else:
            self.close()

if __name__ == '__main__':
    pass
