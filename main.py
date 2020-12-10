#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QTabWidget, QDesktopWidget, QLabel, QCheckBox, QVBoxLayout, QLineEdit, QComboBox, \
    QTableWidget, \
    QWidget, QMainWindow, QApplication, QMessageBox, QStyleFactory, QToolButton, QAction, QInputDialog, QPushButton
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

import sys
import psycopg2

import area_filter
import asterisk_interface
import date_input
import ddns_edit
import html_maker
import label_process
import parameters as gl
import report_lib
import report_tool
import software
import unit
import data_sets

import libpg
import assistencias_pendentes as ass_pendentes
import assistencia as ass
import qlib as qc
import stdio
import ex_grid
import client_edit
import liblogos
import report_display
import classes_un
import un_tags
import models
import login
import hardware
import unit_transfer
from unit_chosse import UnitChoseDialog


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowIcon(QIcon('logos.ico'))
        self.resize(1280, 860)
        self.center()
        self.buttonSize = 100
        # init
        self.report_dict = {'report_id': 0}
        self.tabuladorTabWidget = QTabWidget()
        self.setCentralWidget(self.tabuladorTabWidget)
        self.setWindowTitle('Prism')
        
        if check_alive():
            data_sets.get_params()
            data_sets.get_ds_software_type()
            data_sets.get_unit_files_types()
            data_sets.get_ds_tecnicos()
            data_sets.get_ds_meios()
            data_sets.get_ds_status()
            data_sets.get_os()
            data_sets.get_un_status()
            data_sets.get_hw_status()
            data_sets.get_commit_types()
            data_sets.get_hardware_types()
            data_sets.get_ds_areas()
            data_sets.get_canned_messages_sms()
            data_sets.get_motif_block()
            data_sets.get_proc_types()
            data_sets.get_proc_sources()
            
        else:
            QMessageBox.critical(None,"Erro", "Erro na ligação à Base de Dados")
            sys.exit()
        if int(gl.ds_params['version']) != gl.version:
            QMessageBox.critical(None, "Versão Desactualizada", "Versão da aplicação desactualizada\naperta com o Jorge! ")
            sys.exit()
        if gl.DEVELOP:
            gl.user_dict = data_sets.get_user_data('jorge', '1697')
        else:
            form = login.Login()
            form.exec_()
            if gl.user_dict['user_id'] == 0:
                sys.exit(1)
        # layouts
        self.setWindowTitle('Prism @' + gl.user_dict['user_name'])
        self.mainLayout = QVBoxLayout()
        self.make_tab_units()
        self.tabuladorTabWidget.addTab(self.tab2, 'Unidades')
        self.make_tab_process()
        self.tabuladorTabWidget.addTab(self.tab1, 'Processos')
        self.make_tab_customers()
        self.tabuladorTabWidget.addTab(self.tab4, 'Clientes')
        QApplication.setStyle(QStyleFactory.create('Fusion'))
    
    def make_tab_process(self):
        self.tab1 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab1)

        search_btn = QToolButton()
        search_btn.setIcon(QIcon('.//img//refresh.png'))
        search_btn.setToolTip('Actualiza')
        search_btn.clicked.connect(self.process_grid_refresh)

        self.endedChBox = QCheckBox('Terminadas')
        self.statusCBox = QComboBox()
        self.statusCBox.addItems(gl.ca_status)
        self.statusCBox.currentIndexChanged.connect(self.tags_search_click)
        areasProcTbt = QToolButton()
        areasProcTbt.clicked.connect(self.areas_proc_click)
        self.procTypeCBox = QComboBox()
        self.procTypeCBox.addItems(gl.proc_type)
        self.procTypeCBox.currentIndexChanged.connect(self.proc_type_change)
        
        
        mainTabLayout.addLayout(qc.addHLayout([ search_btn, self.endedChBox, 'Tipo', self.procTypeCBox, 'Zona', areasProcTbt, True]))
        self.gridProcess = QTableWidget()
        self.gridProcess.setSelectionBehavior(QTableWidget.SelectRows)
        self.gridProcess.setSelectionMode(QTableWidget.SingleSelection)
        self.gridProcess.setEditTriggers(QTableWidget.NoEditTriggers)
        self.gridProcess.verticalHeader().setDefaultSectionSize(20)
        self.gridProcess.setAlternatingRowColors(True)
        self.gridProcess.setStyleSheet("alternate-background-color: #e6faff;")
        self.gridProcess.verticalHeader().setVisible(False)
        self.gridProcess.resizeColumnsToContents()
        self.gridProcess.itemDoubleClicked.connect(self.make_proc_from_proc)
        mainTabLayout.addWidget(self.gridProcess)
        ex_grid.grid_process_make_grid(self.gridProcess)
        mainTabLayout.addWidget(self.gridProcess)
        # sub menus
        view_proc = QAction("Ver Processo", self)
        view_proc.setIcon(QIcon('.//img//mk_request.png'))
        view_proc.triggered.connect(self.view_proc_click)
        self.gridProcess.addAction(view_proc)
        showUnitAct = QAction("Ver Unidade", self)
        showUnitAct.setIcon(QIcon('.//img//mk_request.png'))
        showUnitAct.triggered.connect(self.show_unit_from_process)
        self.gridProcess.addAction(showUnitAct)
        
        sp1 = QAction(self)
        sp1.setSeparator(True)
        self.gridProcess.addAction(sp1)
        make_label = QAction("Etiqueta p/ Equipamento", self)
        make_label.setIcon(QIcon('.//img//barcode.png'))
        make_label.triggered.connect(self.make_process_label)
        self.gridProcess.addAction(make_label)
        hw_in_unit = QAction("Equipamentos na Unidade", self)
        hw_in_unit.setIcon(QIcon('.//img//hwd_inventory.png'))
        hw_in_unit.triggered.connect(self.hardware_unit_process)
        self.gridProcess.addAction(hw_in_unit)
        self.gridProcess.setContextMenuPolicy(Qt.ActionsContextMenu)
    
    def tags_search_click(self):
        search_tags = ''
        if not self.tags_search.text() == '':
            search_tags = '\'%%' + self.tags_search.text().lower() + '%%\''
            search_tags = ''' and as_tags like ''' #+ search
        p = ''' assistencias.proc_pendente = True '''
        if self.statusCBox.currentIndex() == 0:
            stat = ' '
        else:
            stat = ''' and as_status like  \'''' + str(self.statusCBox.currentText()) + '\''
        sql = '''SELECT proc_id, to_char(proc_date, 'DD.MM.YYYY') , unidades.un_name, proc_status,
            to_char(EXTRACT(DAY FROM now()-(proc_date)), '9999') AS delay, unidades.un_localidade, proc_unit_id
            from assistencias,unidades
            where ''' + p + stat + search_tags + ''' and unidades.un_id= assistencias.proc_unit_id
            order by proc_date desc'''
        hl = libpg.query_many(sql)
        ex_grid.grid_std(self.gridProcess, data=hl, f_col=['i', 's', 's', 's', 's', 's', 'i'])
    
    def process_grid_refresh(self, data_filter):
        if not data_filter:
            if self.procTypeCBox.currentIndex() > 0:
                data_filter = ' and proc_type= \'''' + self.procTypeCBox.currentText() + '\''''
            else:
                data_filter = ''
            sql = '''select proc_type_key || '-' || proc_id,to_char(proc_date, 'DD-MM-YYYY HH:MM'), un_name,proc_status, unidades.un_localidade, proc_type, proc_unit_id, proc_nivel, proc_reported
             from unidades
             inner join assistencias on proc_unit_id = un_id
             inner join proc_types on proc_type_key=proc_type
                 where proc_pendente = %s ''' + data_filter + ''' order by proc_id desc'''
            hl = libpg.query_many(sql,(not(self.endedChBox.isChecked()),))

        else:
            area = str(data_filter['areas_ids']).replace('[', '(')
            area = area.replace(']',')')
            sql = '''select proc_type_key || '-' || proc_id,to_char(proc_date, 'DD-MM-YYYY HH:MM'), un_name,proc_status, unidades.un_localidade, proc_type, proc_unit_id, proc_nivel, proc_reported
             from unidades
             inner join assistencias on proc_unit_id = un_id
             inner join areas on area_id = unidades.un_area
             inner join proc_types on proc_type_key=proc_type
                    where proc_pendente = %s and proc_area in ''' + area + ''' and
             un_activa = true
             order by area_name, proc_id desc'''
            hl = libpg.query_many(sql,(not(self.endedChBox.isChecked()),))
        ex_grid.process_update_grid(self.gridProcess,hl)
        
    def areas_proc_click(self):
        import area_filter
        form = area_filter.AreaFilter()
        form.exec_()
        if form.ret['responce']:
            self.process_grid_refresh(data_filter=form.ret)


    
    def show_unit_from_process(self):
        unit_id = int(self.gridProcess.item(self.gridProcess.currentRow(), 6).text())
        form = unit.UnitEdit(unit_id)
        form.exec_()
        
    def hardware_unit_process(self):
        try:
            unit_id = int(self.gridProcess.item(self.gridProcess.currentRow(), 6).text())
            un_name = self.gridProcess.item(self.gridProcess.currentRow(), 1).text()
            form = hardware.HardwareBrw({'unit_id': unit_id, 'model_id': 0, 'un_name': un_name, 'edit_mode': True})
            form.exec_()
        except AttributeError:
            pass
        
    
    def make_process_label(self):
        try:
            dum = self.gridProcess.item(self.gridProcess.currentRow(), 0).text().split('-')
            proc_id = int(dum[1])
            form = label_process.ProcessLabel(proc_id)
            form.exec_()
        except (ValueError, IndexError):
            pass
        
    def make_proc_from_unit(self):
        try:
            unit_id = int(self.gridProcess.item(self.gridProcess.currentRow(), 0).text())
            self.make_process(unit_id)
        except (AttributeError, ValueError):
            pass

    def view_proc_click(self):
        try:
            dum = self.gridProcess.item(self.gridProcess.currentRow(), 0).text().split('-')
            proc_id = int(dum[1])
        except (IndexError, ValueError):
             dum = self.gridProcess.item(self.gridProcess.currentRow()-1, 0).text().split('-')
             proc_id = int(dum[1])
        proc_dict = data_sets.process_to_dict(proc_id)
        proc_html = html_maker.process_to_html(proc_dict)
        form = report_display.DisplayReport(proc_html)
        form.exec_()


    def make_proc_from_proc(self):
        """chamada do processo e é este processo que vamos continuar """
        try:
            process_ids = self.gridProcess.item(self.gridProcess.currentRow(), 0).text().split('-')
            process = int(process_ids[1])
        except (AttributeError, ValueError, IndexError):
            process_ids = self.gridProcess.item(self.gridProcess.currentRow()-1, 0).text().split('-')
            process = int(process_ids[1])
        pending_proc = data_sets.assistencia_to_dict(process)
        unit_id = pending_proc['proc_unit_id']
        if pending_proc['proc_pendente']:
            pass
        else:
            pending_proc = {}
        pending_proc['proc_montante'] = process
        if process_ids[0] == 'DDNS':
            """só para ddns para isso vai buscar o setting da unidade."""
            sql = 'select *  from unit_settings where us_unit_id = %s and us_act_id =13'
            dds_setting_data = libpg.query_one(sql, (unit_id,))
            gl.unit_dict = data_sets.unit_to_dic(unit_id)
            form = ddns_edit.DdnsEdit(dds_setting_data, (dds_setting_data[3], dds_setting_data[4]))
            form.exec_()
        else:
            form = ass.Assistencia(pending_proc, unit_id)
            form.exec_()
        gl.asterisk_stack_call = {}
    
    
    
    def proc_type_change(self):
        self.process_grid_refresh(None)
        
    def make_process(self, unit_id):
        """ chamado da unidade """
        # consulta assistencias pendentes
        as_montante = 0
        sql = '''SELECT proc_type_key || '-' || proc_id,proc_date,proc_reported, proc_tecnico, proc_action_report from assistencias
        inner join proc_types on proc_type_key=proc_type
                  WHERE proc_unit_id =%s AND proc_pendente=%s order by proc_date desc'''
        data = (unit_id, True)
        pendentes = libpg.query_many(sql, data)
       
        if len(pendentes) > 0:
            pending = ass_pendentes.PendingProcess(pendentes)
            pending.exec_()
            # pprint.pprint(pending.ret_dict)
            if pending.ret_dict['flag'] == 2: # de outro processo
                # print('de pendente')
                form = ass.Assistencia(pending.ret_dict, unit_id)
                form.exec_()
            elif pending.ret_dict['flag'] == 1: # nova
                # print('nova com pendentes')
                form = ass.Assistencia(pending.ret_dict, unit_id)
                form.exec_()
        else:  # not pending
            form = ass.Assistencia({}, unit_id)
            form.exec_()
        gl.asterisk_stack_call = {}

    
    def make_tab_units(self):
        gl.current_unit = 0
        self.tab2 = QWidget()
        mTabLay = QVBoxLayout(self.tab2)
        self.unitSearchEdt = QLineEdit()
        self.unitSearchEdt.setMaximumWidth(250)
        self.unitSearchEdt.textChanged.connect(self.unit_name_change)
        self.unitActiveCkBox = QCheckBox()
        self.unitActiveCkBox.setChecked(True)
        searchUnitsTBtn = QToolButton()
        searchUnitsTBtn.setIcon(QIcon('.//img//all.png'))
        searchUnitsTBtn.setToolTip('Mostra todos')
        searchUnitsTBtn.clicked.connect(self.units_search_text)
        clearSearchBtn = QToolButton()
        clearSearchBtn.setIcon(QIcon('.//img//clear.png'))
        clearSearchBtn.setToolTip('Limpa pesquisa')
        clearSearchBtn.clicked.connect(self.clear_filters_click)
        printBtn = QToolButton()
        printBtn.setToolTip('Imprime')
        printBtn.setIcon(QIcon('.//img//print.png'))
        printBtn.clicked.connect(self.print_grid_click)
        areasFilterTbt = QPushButton('Zonas')
        areasFilterTbt.setToolTip('Filtra por Zonas')
        areasFilterTbt.setIcon(QIcon('.//img/areas.png'))
        areasFilterTbt.clicked.connect(self.areas_filter_click)
        asteriskLogBtn = QToolButton()
        asteriskLogBtn.setToolTip('Relatório do Asterisk')
        asteriskLogBtn.setIcon(QIcon('.//img//asterisk.png'))
        asteriskLogBtn.clicked.connect(self.asterisk_loc_click)

        self.hamburguer = QLabel()
        pixmap = QPixmap('.//img//hamburger.png')
        self.hamburguer.setPixmap(pixmap)
        # menus do hamburger

        hardwareMangAct = QAction("Gere Hardware", self)
        hardwareMangAct.setIcon(QIcon('.//img//move.png'))
        hardwareMangAct.triggered.connect(self.hw_manager)
        self.hamburguer.addAction(hardwareMangAct)
        
        modelsMangAct = QAction("Gere Modelos", self)
        modelsMangAct.setIcon(QIcon('.//img//move.png'))
        modelsMangAct.triggered.connect(self.models_manager)
        self.hamburguer.addAction(modelsMangAct)

        hw_add_new = QAction("Transfere Hardware", self)
        hw_add_new.setIcon(QIcon('.//img//move.png'))
        hw_add_new.triggered.connect(self.unit_data_transfer)
        self.hamburguer.addAction(hw_add_new)

        self.hamburguer.setContextMenuPolicy(Qt.ActionsContextMenu)
        search_tags_Btn = QToolButton()
        search_tags_Btn.setToolTip('Pesquisa')
        search_tags_Btn.setIcon(QIcon('.//img//search_tags.png'))
        search_tags_Btn.clicked.connect(self.search_tags_mode_click)
        
        clear_tags_Btn = QToolButton()
        clear_tags_Btn.setToolTip('Limpa Tags')
        clear_tags_Btn.setIcon(QIcon('.//img//clear.png'))
        clear_tags_Btn.clicked.connect(self.clear_tags_search)
        
        self.logicTags = QComboBox()
        self.logicTags.setMaximumWidth(80)
        self.logicTags.setMinimumWidth(80)
        self.logicTags.addItems(['OU', 'E'])
        self.logicTags.setCurrentIndex(1)
        self.tags_to_searchEdit = QLineEdit()
        self.tags_browserBtn = QToolButton()
        self.tags_browserBtn.setIcon(QIcon('.//img//tags.png'))
        self.tags_browserBtn.clicked.connect(self.tags_browser_click)       
        mTabLay.addLayout(qc.addHLayout(['Nome', self.unitSearchEdt, 'Activas', self.unitActiveCkBox, searchUnitsTBtn, clearSearchBtn, printBtn,True,
                                         self.logicTags, self.tags_to_searchEdit, self.tags_browserBtn, search_tags_Btn, clear_tags_Btn, True,self.hamburguer]))
        self.reportsGroupCmb = QComboBox()
        self.reportsGroupCmb.currentIndexChanged.connect(self.report_groups_change)
        
        self.reportsGroupCmb.addItems(['','Software','Call Center','Licenças','Equipamentos'])
        mTabLay.addLayout(qc.addHLayout(['Relatórios',self.reportsGroupCmb,areasFilterTbt, asteriskLogBtn, True]))
        self.grid_units = QTableWidget()
        self.grid_units.setSelectionBehavior(QTableWidget.SelectRows)
        self.grid_units.setSelectionMode(QTableWidget.SingleSelection)
        self.grid_units.setEditTriggers(QTableWidget.NoEditTriggers)
        self.grid_units.verticalHeader().setDefaultSectionSize(20)
        self.grid_units.setAlternatingRowColors(True)
        self.grid_units.setStyleSheet("alternate-background-color: #a0d7f5;")
        self.grid_units.verticalHeader().setVisible(False)
        self.grid_units.resizeColumnsToContents()
        ex_grid.make_grid(self.grid_units, headers=['ID', 'Unidade', 'Tipo', 'Localidade', 'C.P.', 'Zona','NIF'],
                          col_width=[(0, 54), (1, 300), (2, 100), (3, 200), (4, 280),(5,220),(6,100)])
        self.grid_units.itemDoubleClicked.connect(self.show_unit)
        mTabLay.addWidget(self.grid_units)
        
        # sub menus
        mk_request = QAction("Cria Pedido", self)
        mk_request.setIcon(QIcon('.//img//mk_request.png'))
        mk_request.triggered.connect(self.make_request)
        self.grid_units.addAction(mk_request)
        open_scall = QAction("Pedidos em aberto", self)
        open_scall.setIcon(QIcon('.//img//prc_open.png'))
        open_scall.triggered.connect(self.scall_open_click)
        self.grid_units.addAction(open_scall)
        closed_scall = QAction("Pedidos terminados", self)
        closed_scall.setIcon(QIcon('.//img//prc_end.png'))
        closed_scall.triggered.connect(self.scall_closed_click)
        
        self.grid_units.addAction(closed_scall)
        
        sp1 = QAction(self)
        sp1.setSeparator(True)
        self.grid_units.addAction(sp1)
        hw_in_unit = QAction("Equipamentos na Unidade", self)
        hw_in_unit.setIcon(QIcon('.//img//hwd_inventory.png'))
        hw_in_unit.triggered.connect(self.hw_in_unit_click)
        self.grid_units.addAction(hw_in_unit)
        self.grid_units.setContextMenuPolicy(Qt.ActionsContextMenu)

    def unit_active_change(self, i):
        print('change')
        
    def search_tags_mode_click(self):
        gl.current_unit = 0
        if not self.tags_to_searchEdit.text() == '':
            sql = self.make_sql_for_tags()
            bc = libpg.query_many(sql, (True,))
            ex_grid.grid_std(self.grid_units, data=bc, f_col=['i', 's', 's', 's', 's'])
            self.grid_units.setHorizontalHeaderLabels(['ID', 'Unidade', 'Tipo', 'Localidade', 'C.P.','Zona'])
        else:
            pass
    
    def make_sql_for_tags(self):
        sql = '''SELECT  un_id, un_name, unit_type.un_type_name,
            un_localidade, un_cp
             FROM unidades, unit_type '''
        tags = str(self.tags_to_searchEdit.text()).replace('\'', '\\\'')
        tags = tags.split(',')
        in_data = ''
        where = 'WHERE '
        if self.logicTags.currentIndex() == 0:  # ou
            for n in tags:
                toto = n.lower().strip()
                in_data += '\'' + toto + '\','
            a = libpg.query_many('''SELECT tau_id from tags_unit where tau_name in (''' + in_data[:-1] + ''')''',
                                 (True,))
            bc = [i for sub in a for i in sub]
            where += '''un_id in(SELECT * from (select tag_unit_id FROM tag_un_refs WHERE tau_tag_id in(''' + \
                     str(bc)[1:-1] + ''')) as foo) AND un_type=unit_type.un_type_id
                and un_activa = ''' + str(self.unitActiveCkBox.isChecked())
        else:
            t = ''
            for n in tags:
                t = t + '\'' + n.strip() + '\','
            t = t[:-1]
            c = str(len(tags))
            where += ''' EXISTS (SELECT NULL
             FROM tag_un_refs tg
             JOIN tags_unit t ON t.tau_id = tg.tau_tag_id
            WHERE t.tau_name IN (''' + t + ''')
              AND tg.tag_unit_id = unidades.un_id
             GROUP BY tg.tag_unit_id
           HAVING COUNT(t.tau_name) =''' + c + ''') and un_type=unit_type.un_type_id
                and un_activa = ''' + str(self.unitActiveCkBox.isChecked())
        
        return sql + where
    
    def clear_tags_search(self):
        self.tags_to_searchEdit.clear()
    
    def tags_browser_click(self):
        form = un_tags.UnitTagsBrowser(mode=2)
        form.exec_()
        if form.tag_list == '':
            pass
        else:
            self.tags_to_searchEdit.setText(form.tag_list[1])
    
    def clear_filters_click(self):
        self.tags_to_searchEdit.clear()
        self.unitActiveCkBox.setCheckState(2)
        self.unitSearchEdt.clear()
        # self.filterByCbx.setCurrentIndex(0)
        self.grid_units.clear()
        ex_grid.grid_std(self.grid_units, data=[], f_col=['i', 's', 's', 's', 's'])
        self.grid_units.setHorizontalHeaderLabels(['ID', 'Unidade', 'Tipo', 'Localidade', 'C.P.','Zona'])
    
    
    def report_groups_change(self):
        rpt_index = self.reportsGroupCmb.currentIndex()
        repor_dict = {1:'SOFT', 2:'CALL',3: 'LIC', 4:'MOD'}
        if rpt_index >0:
            form = report_tool.ReportTool(repor_dict[rpt_index])
            form.exec_()
            self.reportsGroupCmb.setCurrentIndex(0)
        
    def areas_filter_click(self):
        form = area_filter.AreaFilter()
        form.exec_()
        ret = form.ret
        if ret['responce']:
            f = str(ret['areas_ids'])
            f = f.replace('[','(')
            f = f.replace(']',')')
            names = str(ret['areas_names'])
            names = names.replace('[','')
            names = names.replace(']','')
            names = names.replace('\'','')
            # self.filterLabel.setText(names)
            sql = '''SELECT  un_id, un_name, unit_type.un_type_name, un_localidade, un_cp , area_name
                    FROM unidades
                    INNER JOIN unit_type on unit_type.un_type_id = unidades.un_type
                    INNER JOIN areas on areas.area_id=unidades.un_area
                    WHERE
                          unidades.un_area in ''' + f + ''' AND un_activa = true
                    ORDER BY area_name '''
            bc = libpg.query_many(sql, (True,))
            ex_grid.grid_std(self.grid_units, data=bc, f_col=['i', 's', 's', 's', 's','s'])
            self.grid_units.setHorizontalHeaderLabels(['ID', 'Unidade', 'Tipo', 'Localidade', 'C.P.','Zona'])
    
    
    def asterisk_loc_click(self):
        form = asterisk_interface.AsteriskInterface()
        form.exec_()
        gl.asterisk_stack_call = form.toto
        # gl.asterisk_stack_call['call_number'] == '':
        if gl.asterisk_stack_call == {}:
            pass
        else:
            sql = '''select distinct un_id, un_name
                    from contacts
                    inner join unidades on un_id=contacts.ct_unit
                    where un_activa=True and  ct_value2 = %s GROUP BY un_id, un_name order by un_name'''
            units_in_contact = libpg.query_many(sql, (gl.asterisk_stack_call['call_number'],))
            if len(units_in_contact) == 0:
                pass
            elif len(units_in_contact) == 1:
                self.make_process(units_in_contact[0][0])
            else:
                form = UnitChoseDialog(units_in_contact)
                form.exec_()
                if form.ret[0]:
                    self.make_process(form.ret[1])
    
    
    def print_grid_click(self):
        data_set = []
        for linha in range(0, self.grid_units.rowCount()):
            dum = (self.grid_units.item(linha,0).text(),)
            for col in range(1, self.grid_units.columnCount()):
                dum = dum + (self.grid_units.item(linha,col).text(),)
            data_set.append(dum)
            
        header = []
        for n in range(0,self.grid_units.columnCount()):
            header.append(self.grid_units.horizontalHeaderItem(n).text())
        proc_html = report_lib.unit_grid_report(data_set,header)
        form = report_display.DisplayReport(proc_html)
        form.exec_()
    
    def unit_name_change(self, tx):
        gl.current_unit = 0
        if len(tx) > 2:
            search = '\'%%' + tx.lower() + '%%\''
            self.units_seach_inc(tx=search)
    
    def units_seach_inc(self, tx='', client=0):
        sql = '''SELECT  un_id, un_name, unit_type.un_type_name,
            un_localidade, un_cp, area_name, cl_nif
             FROM unidades,  unit_type, areas, clientes
             WHERE un_type=unit_type.un_type_id and un_area=area_id AND cl_id=un_cliente_id and
             un_activa = ''' + str(self.unitActiveCkBox.isChecked())
        if not tx == '':
            sql += ''' AND unaccent(LOWER(un_name)) LIKE ''' + tx
        if client > 0:
            sql += ''' and un_cliente_id= ''' + str(client)
        sql += ''' ORDER BY un_name'''
        bc = libpg.query_many(sql, (True,))
        ex_grid.grid_std(self.grid_units, data=bc, f_col=['i', 's', 's', 's', 's','s','s'])
    
    def units_search_text(self):
        search = '\'%%' + self.unitSearchEdt.text().lower() + '%%\''
        sql = '''SELECT  un_id, un_name, unit_type.un_type_name,
            un_localidade, un_cp, area_name,cl_nif
             FROM unidades,  unit_type, areas, clientes
             WHERE  un_type=unit_type.un_type_id
                and un_area=area_id AND cl_id=un_cliente_id
                AND un_activa = ''' + str(self.unitActiveCkBox.isChecked())
        sql += ''' AND unaccent(LOWER(un_name)) LIKE ''' + search
        sql += ''' ORDER BY un_name'''
        bc = libpg.query_many(sql, (True,))
        ex_grid.grid_std(self.grid_units, data=bc, f_col=['i', 's', 's', 's', 's','s','s'])
        self.grid_units.setHorizontalHeaderLabels(['ID', 'Unidade', 'Tipo', 'Localidade', 'C.P.','Zona'])
        
    def show_unit(self):
        b = int(self.grid_units.item(self.grid_units.currentRow(), 0).text())
        form = unit.UnitEdit(b)
        form.exec_()
    
    def hw_in_unit_click(self):
        try:
            b = int(self.grid_units.item(self.grid_units.currentRow(), 0).text())
            un_name = self.grid_units.item(self.grid_units.currentRow(), 1).text()
            form = hardware.HardwareBrw({'unit_id': b, 'model_id': 0, 'un_name': un_name, 'edit_mode': True})
            form.exec_()
        except AttributeError:
            pass
    
    # def make_report(self):
    #     form = reports_interfaces.ReportInterface()
    #     form.exec_()
    #     self.report_dict = form.ret
    #     if self.report_dict['responce']:
    #         self.filter_by_change()
            
    def refresh_report(self):
        if self.report_dict['report_id'] > 0:
            self.filter_by_change()
        else:
            self.make_report()
            
    def filter_by_change(self):
        if self.report_dict['report_id'] == 1:
            form = models.ModelsBrowser({'mode': 1})
            form.exec_()
            form.ret['model_id'] = form.ret.get('model_id', 0)
            if form.ret['model_id'] > 0:
                sql = '''SELECT  un_id, un_name, unit_type.un_type_name, un_localidade, un_cp
                     FROM unidades, unit_type,hardware
                      where unidades.un_id=hardware.hw_unit_id and un_type=unit_type.un_type_id AND
                      hardware.hw_model_id=%s'''
                sql += ''' ORDER BY un_name'''
                bc = libpg.query_many(sql, (form.ret['model_id'],))
                ex_grid.grid_std(self.grid_units, data=bc, f_col=['i', 's', 's', 's', 's'])
                self.filterLabel.setText(self.report_dict['report_name'] + ':' + form.ret['brand_name'] + ':' + form.ret['model_name'] + ':' + form.ret['hw_type_name'])
        elif self.report_dict['report_id'] == 2:
            """unidades por softwate"""
            form = software.SoftwareBrowser({'un_type': 0})
            form.exec_()
            if form.ret[0]:
                sql = ''' SELECT  un_id, un_name, 'n/d',un_localidade, un_cp, area_name
                     FROM unit_settings
                     inner join unidades on unidades.un_id = unit_settings.us_unit_id
                     inner join areas  on areas.area_id = unidades.un_area
                     where unit_settings.us_act_id=1 and lower(us_value1) = %s and lower(us_value2) = %s and  unidades.un_activa = %s'''
                sql += ''' ORDER BY un_name '''
                xl = libpg.query_many(sql, (form.ret[1].lower(), form.ret[2].lower(), str(self.unitActiveCkBox.isChecked())))
                ex_grid.grid_std(self.grid_units, data=xl, f_col=['i', 's', 's', 's', 's','s'])
                self.filterLabel.setText(self.report_dict['report_name'] + ':' + form.ret[1] + ':' + form.ret[2])
        elif self.report_dict['report_id'] == 3:
            form = date_input.DateInput(self.report_dict['report_name'])
            form.exec_()
            if form.ret[0]:
                sql = '''SELECT cm_unit_id, unidades.un_name,'N/D',un_localidade,
                         comitments_unit.cm_value,(to_date(comitments_unit.cm_value, 'YYYY-MM-DD') - DATE 'now') as s
                        FROM comitments_unit,unidades
                        WHERE  comitments_unit.cm_act_id=15 and cm_archive = False
                        and (to_date(comitments_unit.cm_value, 'YYYY-MM-DD') >= %s
                        and to_date(comitments_unit.cm_value, 'YYYY-MM-DD') <=%s)
                        and unidades.un_id= comitments_unit.cm_unit_id and
                        un_activa = True
                        order by s asc'''
                xl = libpg.query_many(sql, (form.ret[1],form.ret[2]))
                ex_grid.grid_std(self.grid_units, data=xl, f_col=['i', 's', 's', 's', 's'])
                self.grid_units.setHorizontalHeaderLabels(['ID', 'Unidade', 'Tipo', 'Localidade', 'Data','Zona'])
                self.filterLabel.setText(self.report_dict['report_name'] + ' de' + form.ret[1] + ' a ' + form.ret[2])
        elif self.report_dict['report_id'] == 4: # validade da licença
            form = date_input.DateInput(self.report_dict['report_name'])
            form.exec_()
            if form.ret[0] :
                sql = '''SELECT cm_unit_id, unidades.un_name,'N/D',un_localidade,
                          comitments_unit.cm_value,(to_date(comitments_unit.cm_value, 'YYYY-MM-DD') - DATE 'now') as s
                         FROM comitments_unit,unidades
                         WHERE  comitments_unit.cm_act_id=14 and cm_archive = False
                         and (to_date(comitments_unit.cm_value, 'YYYY-MM-DD') >= %s
                         and to_date(comitments_unit.cm_value, 'YYYY-MM-DD') <= %s)
                         and unidades.un_id= comitments_unit.cm_unit_id and un_activa=True
                         order by s asc'''
                xl = libpg.query_many(sql,(form.ret[1],form.ret[2]))
                ex_grid.grid_std(self.grid_units, data=xl, f_col=['i', 's', 's', 's', 's'])
                self.grid_units.setHorizontalHeaderLabels(['ID', 'Unidade', 'Tipo', 'Localidade', 'Data','Zona'])
                self.filterLabel.setText(self.report_dict['report_name'] + ' de ' + form.ret[1] + ' a ' + form.ret[2])
        elif self.report_dict['report_id'] == 5: # eorder
            form = date_input.DateInput(self.report_dict['report_name'])
            form.exec_()
            if form.ret[0] :
                sql = '''SELECT cm_unit_id, unidades.un_name,'N/D',un_localidade,
                          comitments_unit.cm_value,(to_date(comitments_unit.cm_value, 'YYYY-MM-DD') - DATE 'now') as s
                         FROM comitments_unit,unidades
                         WHERE  comitments_unit.cm_act_id=24 and cm_archive = False
                         and ( to_date(comitments_unit.cm_value, 'YYYY-MM-DD') >= %s
                         and to_date(comitments_unit.cm_value, 'YYYY-MM-DD') <=%s)
                         and unidades.un_id= comitments_unit.cm_unit_id and un_activa=True
                         order by s asc'''
                xl = libpg.query_many(sql, (form.ret[1],form.ret[2]))
                ex_grid.grid_std(self.grid_units, data=xl, f_col=['i', 's', 's', 's', 's'])
                self.grid_units.setHorizontalHeaderLabels(['ID', 'Unidade', 'Tipo', 'Localidade', 'Data','Zona'])
                self.filterLabel.setText(self.report_dict['report_name'] + ' de ' + form.ret[1] + ' a ' + form.ret[2])
        elif self.report_dict['report_id'] == 6: # software a Bloqueiar chave=13
            form = date_input.DateInput(self.report_dict['report_name'])
            form.exec_()
            if form.ret[0] :
                sql = '''SELECT cm_unit_id, unidades.un_name,'N/D',un_localidade,
                          comitments_unit.cm_value,(to_date(comitments_unit.cm_value, 'YYYY-MM-DD') - DATE 'now') as s
                         FROM comitments_unit,unidades
                         WHERE  comitments_unit.cm_act_id=13 and cm_archive = False
                         and (to_date(comitments_unit.cm_value, 'YYYY-MM-DD') >= %s
                         and to_date(comitments_unit.cm_value, 'YYYY-MM-DD') <= %s)
                         and unidades.un_id= comitments_unit.cm_unit_id and un_activa=True
                         order by s asc'''
                xl = libpg.query_many(sql,(form.ret[1],form.ret[2]))
                ex_grid.grid_std(self.grid_units, data=xl, f_col=['i', 's', 's', 's', 's'])
                self.grid_units.setHorizontalHeaderLabels(['ID', 'Unidade', 'Tipo', 'Localidade', 'Data','Zona'])
                self.filterLabel.setText(self.report_dict['report_name'] + ' de ' + form.ret[1] + ' a ' + form.ret[2])

    def hw_manager(self):
        form = hardware.HardwareBrw({'unit_id': 0, 'model_id': 0, 'edit_mode': True})
        form.exec_()
    
    def models_manager(self):
        form = models.ModelsBrowser({'mode': 0})
        form.exec_()
    
    def unit_data_transfer(self):
        form = unit_transfer.UnitTransfer()
        form.exec_()
        
    def make_tab_customers(self):
        self.tab4 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab4)
        self.cl_name = QLineEdit()
        self.cl_name.setMaximumWidth(300)
        self.cl_name.textChanged.connect(self.customer_name_change)
        
        self.cl_nif = QLineEdit()
        self.cl_nif.setMaximumWidth(100)
        self.cl_nif.textChanged.connect(self.customer_nif_change)
        
        self.cl_active = QCheckBox()
        self.cl_active.setChecked(True)
        search_customers = QToolButton()
        search_customers.setIcon(QIcon('.//img//all.png'))
        search_customers.clicked.connect(self.customer_refresh)
        self.orderByCbox = QComboBox()
        self.orderByCbox.addItems(['Nome','Numero','Localidade','C.C.'])
        self.orderByCbox.currentIndexChanged.connect(self.customer_refresh)
        
        mainTabLayout.addLayout(qc.addHLayout(['Nome', self.cl_name, 'NIF', self.cl_nif, 'Activos', self.cl_active, search_customers, True,'Ordena', self.orderByCbox]))
        self.gridCustomers = QTableWidget()
        self.gridCustomers.setSelectionBehavior(QTableWidget.SelectRows)
        self.gridCustomers.setSelectionMode(QTableWidget.SingleSelection)
        self.gridCustomers.setEditTriggers(QTableWidget.NoEditTriggers)
        self.gridCustomers.verticalHeader().setDefaultSectionSize(20)
        self.gridCustomers.setAlternatingRowColors(True)
        self.gridCustomers.setStyleSheet("alternate-background-color: #e6e6ff;")
        self.gridCustomers.verticalHeader().setVisible(False)
        self.gridCustomers.resizeColumnsToContents()
        
        self.gridCustomers.itemDoubleClicked.connect(self.customer_click)
        
        mainTabLayout.addWidget(self.gridCustomers)
        ex_grid.make_grid(self.gridCustomers, headers=['ID', 'Nome', 'Localidade', 'NIF', 'C.P.', 'C.C.'], col_width=[(0, 88), (1, 378), (2, 200), (3, 100), (4, 220), (5, 70)])
        # self.customer_refresh()
        add_customer = QAction("Adiciona Cliente", self)
        add_customer.setIcon(QIcon('.//img//mk_request.png'))
        add_customer.triggered.connect(self.add_customer_click)
        self.gridCustomers.addAction(add_customer)
        
        sp1 = QAction(self)
        sp1.setSeparator(True)
        self.gridCustomers.addAction(sp1)
        
        add_unit = QAction("Adiciona Unidade", self)
        add_unit.setIcon(QIcon('.//img//mk_request.png'))
        add_unit.triggered.connect(self.add_unit_click)
        
        self.gridCustomers.addAction(add_unit)
        show_units = QAction("Mostra Unidades", self)
        show_units.setIcon(QIcon('.//img//mk_request.png'))
        show_units.triggered.connect(self.show_units_click)
        
        self.gridCustomers.addAction(show_units)
        self.gridCustomers.setContextMenuPolicy(Qt.ActionsContextMenu)
    
    def customer_refresh(self):
        sql = '''SELECT cl_id , cl_nome, cl_localidade, cast(cl_nif as text), cl_cp, cl_cc
                FROM clientes where cl_active = %s order by ''' + gl.client_sort_dict[self.orderByCbox.currentIndex()]
        hl = libpg.query_many(sql, (self.cl_active.isChecked(),))
        ex_grid.grid_std(self.gridCustomers, data=hl, f_col=['i', 's', 's', 's', 's', 'd2'])
    
    def customer_name_change(self):
        tx = self.cl_name.text().lower()
        if len(tx) > 3:
            search = '\'%%' + tx + '%%\''
            sql = '''SELECT cl_id , cl_nome, cl_localidade, CAST (cl_nif as TEXT), cl_cc
                      FROM clientes where unaccent(LOWER(cl_nome)) LIKE ''' + search + ' and cl_active = ' + str(
                self.cl_active.isChecked()) + ' order by cl_nome'
            bc = libpg.sql_query(sql)
            ex_grid.grid_std(self.gridCustomers, data=bc, f_col=['i', 's', 's', 's', 'd2'])
    
    def customer_nif_change(self):
        tx = self.cl_nif.text().lower()
        if len(tx) > 2:
            search = '\'%%' + tx + '%%\''
            sql = '''SELECT cl_id , cl_nome, cl_localidade, cast(cl_nif as TEXT), cl_cc
                      FROM clientes where cl_nif LIKE ''' + search + ' and cl_active = ' + str(
                self.cl_active.isChecked()) + ' order by cl_nome'
            bc = libpg.sql_query(sql)
            ex_grid.grid_std(self.gridCustomers, data=bc, f_col=['i', 's', 's', 's', 'd2'])
    
    def customer_click(self):
        b = int(self.gridCustomers.item(self.gridCustomers.currentRow(), 0).text())
        form = client_edit.EditClient(b)
        form.exec_()
        if form.ret[0]:
            self.units_seach_inc(client=b)
            self.tabuladorTabWidget.setCurrentIndex(0)
    
    def add_customer_click(self):
        form = client_edit.EditClient(-1)
        form.exec_()
    
    def add_unit_click(self):
        b = int(self.gridCustomers.item(self.gridCustomers.currentRow(), 0).text())
        form = classes_un.UnitAdd(b)
        form.exec_()
    
    def show_units_click(self):
        b = int(self.gridCustomers.item(self.gridCustomers.currentRow(), 0).text())
        self.units_seach_inc(client=b)
        self.tabuladorTabWidget.setCurrentIndex(0)
       
    def br_add_click(self):
        pass
    
    def md_add_click(self):
        form = models.ModelEdit(-1, gl.brand_id)
        form.exec_()
        self.brand_drill_down_click()
    
    def md_edit_click(self):
        a = int(self.grid_models.item(self.grid_models.currentRow(), 0).text())
        form = models.ModelEdit(a, gl.brand_id)
        form.exec_()
        self.brand_drill_down_click()
    
    def hw_goto_unit_click(self):
        b = int(self.grid_hardware.item(self.grid_hardware.currentRow(), 5).text())
        form = unit.UnitEdit(b)
        form.exec_()
    
    def hw_refresh(self):
        self.call_debug()
    
    def make_tab_software(self):
        self.tab7 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab7)
    
    def exit_click(self):
        self.close()
    
    def make_request(self):
        unit_id = int(self.grid_units.item(self.grid_units.currentRow(), 0).text())
        if liblogos.get_install_date(unit_id):
            self.make_process(unit_id)
        else:
            QMessageBox.critical(None,"Asneira","Esta unidade ainda não foi instalada :-)")
    
    def scall_open_click(self):
        unit_id = int(self.grid_units.item(self.grid_units.currentRow(), 0).text())
        sql = '''select proc_type_key || '-' || proc_id, to_char(proc_date,
                'DD-MM-YYYY HH:MM'), un_name, proc_status, unidades.un_localidade, proc_type, proc_unit_id, proc_nivel, proc_reported
        from unidades
        inner join assistencias on proc_unit_id = un_id
        inner join proc_types on proc_type_key=proc_type
        where
        proc_pendente = True and proc_unit_id =%s and unidades.un_id= assistencias.proc_unit_id
            order by proc_date desc'''
        hl = libpg.query_many(sql, (unit_id,))
        ex_grid.process_update_grid(self.gridProcess,hl)
        self.tabuladorTabWidget.setCurrentIndex(1)
    
    def scall_closed_click(self):
        unit_id = int(self.grid_units.item(self.grid_units.currentRow(), 0).text())
        sql = '''select proc_id, to_char(proc_date,
                'DD-MM-YYYY HH:MM'), un_name, proc_status, unidades.un_localidade, proc_type, proc_unit_id, proc_nivel, proc_reported
        from unidades
        inner join assistencias on proc_unit_id = un_id
        where
        proc_pendente = False and proc_unit_id =%s and unidades.un_id= assistencias.proc_unit_id
            order by proc_date desc'''
        hl = libpg.query_many(sql, (unit_id,))
        ex_grid.process_update_grid(self.gridProcess,hl)
        self.tabuladorTabWidget.setCurrentIndex(1)
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def call_debug(self):
        import imp
        foo = imp.load_source('grid_tools', '../tools/grid_tools.py')
        foo.calc_grid_width(grid_obj=self.gridProcess, name='self.grid_open_p', types=True)


def check_alive():
    gl.conn_string = "host=" + gl.db_host + " dbname=" + gl.db_database + " port=" + gl.db_port + " user=" + gl.db_user + " password=" + gl.db_password

    try:
        conn = psycopg2.connect(gl.conn_string)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute('Select * from unidades')
        # print('ligado a', gl.db_host)
        return True
    except Exception as e:  # psycopg2.DatabaseError:
        stdio.log_write('update.log', str(e))
        if str(e).find('not connect') > -1:
            print('Não consegui ligar ao servidor: ' + gl.db_host)
        else:
            print('Erro desconhecido:\n' + str(e))
        print('------DEBUG-------------')
        print(str(e))
        return False


def main():
    gl.error_stack = ' '
    gl.dos = False
    if sys.platform == 'win32':
        gl.dos = True
    # try:
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()
    liblogos.log_actions(gl.user_dict,'logout')
    # except Exception, err:
    #     print "Erro no main"
    #     print str(Exception) + '\n'  + str(err)
    #     stdio.print2file('erro.log','Erro\n' + str(Exception)+ '\n' + str(err))
    #     sys.exit()


main()
