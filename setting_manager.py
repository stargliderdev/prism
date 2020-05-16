#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QTableWidget, QPushButton, QHBoxLayout, QApplication, \
    QToolButton, QMessageBox
import sys

import data_sets
import ex_grid
import libpg
import qlib as qc
import models_lib
import parameters as gl


class SeetingsManager(QDialog):
    def __init__(self, parent=None):
        super(SeetingsManager, self).__init__(parent)
        self.resize(1024, 650)
        self.setWindowTitle('Paramateros por Tipo de unidade')
        # self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
        masterLayout = QVBoxLayout(self)
        self.ret = {}
        self.settingTypeCBox = QComboBox()
        self.settingTypeCBox.setMaximumWidth(200)
        self.settingTypeCBox.addItems(['Configurações','Compromissos',])
        # self.settingTypeCBox.textChanged.connect(self.brand_search_changed)
        closeBtn = QPushButton()
        closeBtn.setText('Sair')
        closeBtn.setFocusPolicy(0)  # Qt.NoFocus
        closeBtn.clicked.connect(self.exit_click)
        masterLayout.addLayout(qc.addHLayout([self.settingTypeCBox, True, closeBtn]))
        gridContainLayout = QHBoxLayout()
        self.unitTypesGrid = QTableWidget()
        self.unitTypesGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.unitTypesGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.unitTypesGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.unitTypesGrid.verticalHeader().setDefaultSectionSize(20)
        self.unitTypesGrid.verticalHeader().setVisible(False)
        self.unitTypesGrid.resizeColumnsToContents()
        self.unitTypesGrid.setMaximumWidth(200)
        self.unitTypesGrid.setAlternatingRowColors(True)
        self.unitTypesGrid.setStyleSheet("alternate-background-color: #e6ffff;")
        self.unitTypesGrid.itemDoubleClicked.connect(self.settings_refresh)
        gridContainLayout.addWidget(self.unitTypesGrid)
        
        self.settingsInTypeGrid = QTableWidget()
        self.settingsInTypeGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.settingsInTypeGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.settingsInTypeGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.settingsInTypeGrid.verticalHeader().setDefaultSectionSize(20)
        self.settingsInTypeGrid.verticalHeader().setVisible(False)
        self.settingsInTypeGrid.resizeColumnsToContents()
        self.settingsInTypeGrid.setAlternatingRowColors(True)
        self.settingsInTypeGrid.setStyleSheet("alternate-background-color: #e6fff2;")
        addModel = QToolButton()
        addModel.setText('+')
        addModel.clicked.connect(self.add_setting_to_unit)
        removeModel = QToolButton()
        removeModel.setText('-')
        removeModel.clicked.connect(self.settings_delete)
        
        dum2Layout = QVBoxLayout()
        dum2Layout.addWidget(self.settingsInTypeGrid)
        dum2Layout.addLayout(qc.addHLayout([addModel, removeModel, True]))
        gridContainLayout.addLayout(dum2Layout)
        masterLayout.addLayout(gridContainLayout)
        exit_btn = QPushButton('Sair')
        exit_btn.clicked.connect(self.exit_click)
        self.units_type_refresh()
    
    def settings_refresh(self):
        b = int(self.unitTypesGrid.item(self.unitTypesGrid.currentRow(), 0).text())
        setting_type = self.settingTypeCBox.currentIndex()
        if setting_type== 0 :
            sql = '''select un_type_ref_id, ust_name from unit_types_ref, us_types
                    where unit_types_ref.un_type_ref_setting_id=us_types.ust_id and unit_types_ref.un_type_ref_unit_type=%s and un_type_ref_class = %s   '''
            dataset = libpg.query_many(sql, (b, setting_type))
        else:
            sql = '''select un_type_ref_id, cmt_name from unit_types_ref, comit_types
                                where unit_types_ref.un_type_ref_setting_id=comit_types.cmt_id and unit_types_ref.un_type_ref_unit_type=%s and un_type_ref_class = %s   '''
            dataset = libpg.query_many(sql, (b, setting_type))
        
        ex_grid.ex_grid_update(self.settingsInTypeGrid,
                               {0: ['ID', 'i'], 1: ['Nome','s']}, dataset, hidden=0)
        # self.settingsInTypeGrid.setColumnWidth(0, 80)
        self.settingsInTypeGrid.setColumnWidth(1, 200)
    
    # def model_edit_click(self):
    #     if self.settings['mode'] == 0:
    #         model = int(self.settingsInTypeGrid.item(self.settingsInTypeGrid.currentRow(), 0).text())
    #         brand_id = int(self.unitTypesGrid.item(self.unitTypesGrid.currentRow(), 0).text())
    #         brand_name = self.unitTypesGrid.item(self.unitTypesGrid.currentRow(), 1).text()
    #         form = models_lib.ModelEdit(model, brand_id, brand_name)
    #         form.exec()
    #         self.settings_refresh()
    #     else:
    #         model = int(self.settingsInTypeGrid.item(self.settingsInTypeGrid.currentRow(), 0).text())
    #         model_txt = self.settingsInTypeGrid.item(self.settingsInTypeGrid.currentRow(), 1).text()
    #         brand_id = int(self.unitTypesGrid.item(self.unitTypesGrid.currentRow(), 0).text())
    #         brand_name = self.unitTypesGrid.item(self.unitTypesGrid.currentRow(), 1).text()
    #         hardware_type = self.settingsInTypeGrid.item(self.settingsInTypeGrid.currentRow(), 2).text()
    #         self.ret = {'model_id': model, 'brand_id': brand_id, 'brand_name': brand_name, 'model_name': model_txt,
    #                     'hw_type_name': hardware_type}
    #         self.close()
    
    def add_setting_to_unit(self):
        try:
            unit_type = int(self.unitTypesGrid.item(self.unitTypesGrid.currentRow(), 0).text())
            if self.settingTypeCBox.currentIndex() == 0:
                form = ShowSettingsBrowser()
                form.exec_()
                if form.ret['ust_id'] > 0:
                    print('insert ', unit_type, 'in', form.ret['ust_id'])
                    libpg.execute_query(
                        'DELETE FROM unit_types_ref WHERE un_type_ref_unit_type= %s and un_type_ref_setting_id=%s',
                        (unit_type, form.ret['ust_id']))
                    libpg.execute_query(
                        'INSERT INTO unit_types_ref (un_type_ref_class, un_type_ref_unit_type, un_type_ref_setting_id) values (0,%s,%s)',
                        (unit_type, form.ret['ust_id']))

            elif self.settingTypeCBox.currentIndex() == 1:
                form = ShowCommitementsBrowser()
                form.exec_()
                if form.ret['cmt_id'] >0:
                    print('insert ', unit_type,'in', form.ret['cmt_id'])
                    libpg.execute_query('DELETE FROM unit_types_ref WHERE un_type_ref_unit_type= %s and un_type_ref_setting_id=%s', (unit_type,form.ret['cmt_id']))
                    libpg.execute_query('INSERT INTO unit_types_ref (un_type_ref_class, un_type_ref_unit_type, un_type_ref_setting_id) values (1,%s,%s)', (unit_type,form.ret['cmt_id']))
            self.settings_refresh()
        except AttributeError:
            QMessageBox.warning(None, "Erro", "Escolher o tipo de unidade!")

    def settings_delete(self):
        try:
            # unit_type = int(self.unitTypesGrid.item(self.unitTypesGrid.currentRow(), 0).text())
            un_type_ref_id = int(self.settingsInTypeGrid.item(self.settingsInTypeGrid.currentRow(), 0).text())
            if un_type_ref_id > 0:
                print('delete', un_type_ref_id)
                libpg.execute_query('DELETE FROM unit_types_ref WHERE un_type_ref_id=%s', (un_type_ref_id,))
                self.settings_refresh()
            else:
                pass
        except AttributeError:
            pass
    
    def units_type_refresh(self):
        sql = '''select un_type_id,un_type_name from unit_type where un_type_active = True order by un_type_id '''
        dataset = libpg.query_many(sql, True)
        ex_grid.ex_grid_update(self.unitTypesGrid, {0: ['ID', 'i'], 1: ['Tipo', 's']}, dataset, hidden=0)
        self.unitTypesGrid.setColumnWidth(1, 200)
    
    def exit_click(self):
        self.close()


class ShowCommitementsBrowser(QDialog):
    def __init__(self, parent=None):
        super(ShowCommitementsBrowser, self).__init__(parent)
        masterLayout = QVBoxLayout(self)
        self.ret = {'cmt_id': 0}
        self.resize(600, 300)
        self.setWindowTitle('Adiciona Tipo de compromisso')
        self.commiGrid = QTableWidget()
        self.commiGrid.itemDoubleClicked.connect(self.add_commit_click)
        
        self.commiGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.commiGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.commiGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.commiGrid.verticalHeader().setDefaultSectionSize(20)
        self.commiGrid.setAlternatingRowColors(True)
        self.commiGrid.setStyleSheet("alternate-background-color: #89CFF0;")
        self.commiGrid.verticalHeader().setVisible(False)
        
        ex_grid.make_grid(self.commiGrid, ['cm_id', 'Nome'], [(0, 0), (1, 270)])
        masterLayout.addWidget(self.commiGrid)
        hl = libpg.query_many('''SELECT cmt_id, cmt_name
        FROM comit_types where cmt_active=True
          ORDER BY cmt_group, cmt_order''', (True,))
        ex_grid.grid_std(self.commiGrid, data=hl, f_col=['i', 's'])
    
    def add_commit_click(self):
        self.ret = {'cmt_id': int(self.commiGrid.item(self.commiGrid.currentRow(), 0).text())}
        self.close()


class ShowSettingsBrowser(QDialog):
    def __init__(self, parent=None):
        super(ShowSettingsBrowser, self).__init__(parent)
        masterLayout = QVBoxLayout(self)
        self.ret = {'ust_id': 0}
        self.resize(600, 300)
        self.setWindowTitle('Adiciona Tipo de Configuração')
        self.settingsGrid = QTableWidget()
        self.settingsGrid.itemDoubleClicked.connect(self.add_commit_click)
        
        self.settingsGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.settingsGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.settingsGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.settingsGrid.verticalHeader().setDefaultSectionSize(20)
        self.settingsGrid.setAlternatingRowColors(True)
        self.settingsGrid.setStyleSheet("alternate-background-color: #89CFF0;")
        self.settingsGrid.verticalHeader().setVisible(False)
        
        ex_grid.make_grid(self.settingsGrid, ['cm_id', 'Nome'], [(0, 0), (1, 270)])
        masterLayout.addWidget(self.settingsGrid)
        hl = libpg.query_many('''SELECT ust_id, ust_name
        FROM us_types where ust_active = True
          ORDER BY ust_group, ust_order''', (True,))
        ex_grid.grid_std(self.settingsGrid, data=hl, f_col=['i', 's'])
    
    def add_commit_click(self):
        self.ret = {'ust_id': int(self.settingsGrid.item(self.settingsGrid.currentRow(), 0).text())}
        self.close()

def main():
    gl.user_dict = data_sets.get_user_data('jorge', '1697')
    app = QApplication(sys.argv)
    form = SeetingsManager()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()