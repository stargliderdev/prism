#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, \
    QMessageBox, QTableWidget

import classes_un
import ddns_edit
import ex_grid
import liblogos
import libpg
import software
import parameters as gl

class AddSettingBrowser(QDialog):
    def __init__(self, unit_id, unit_type, parent=None):
        super(AddSettingBrowser, self).__init__(parent)
        masterLayout = QVBoxLayout(self)
        self.resize(400, 450)
        self.toto = None
        self.unit_id = unit_id
        self.unit_type = unit_type
        self.setWindowTitle('Adicionar Configuração')
        self.settings_grid = QTableWidget()
        self.settings_grid.itemDoubleClicked.connect(self.new_setting_click)
        
        self.settings_grid.setSelectionBehavior(QTableWidget.SelectRows)
        self.settings_grid.setSelectionMode(QTableWidget.SingleSelection)
        self.settings_grid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.settings_grid.verticalHeader().setDefaultSectionSize(20)
        self.settings_grid.setAlternatingRowColors(True)
        self.settings_grid.setStyleSheet("alternate-background-color: #d9f2e6;")
        self.settings_grid.verticalHeader().setVisible(False)
        
        ex_grid.make_grid(self.settings_grid, ['us_id', 'Nome'], [(0, 0), (1, 270)])
        masterLayout.addWidget(self.settings_grid)
        sql = '''select unit_set_id,unit_set_name,unit_set_order,unit_set_group,unit_set_multi
                from unit_types_ref, unit_set_types
                where un_type_ref_class=0 and un_type_ref_unit_type =%s and un_type_ref_setting_id=unit_set_types.unit_set_id order by unit_set_name'''
        hl = libpg.query_many(sql, (unit_type,))
        ex_grid.grid_std(self.settings_grid, data=hl, f_col=['i', 's'])
        cancelBtn = QPushButton('Esquece')
        cancelBtn.clicked.connect(self.cancel_click)
        masterLayout.addWidget(cancelBtn)
    
    def cancel_click(self):
        self.close()
    
    def new_setting_click(self):
        """adiciona settings"""
        setting_id = int(self.settings_grid.item(self.settings_grid.currentRow(), 0).text())
        title = self.settings_grid.item(self.settings_grid.currentRow(), 1).text()
        current_settting = libpg.query_one('''SELECT unit_set_types.unit_set_name,  unit_set_types.unit_set_multi
                FROM unit_settings
                INNER JOIN unit_set_types ON (unit_settings.us_act_id = unit_set_types.unit_set_id)
                WHERE unit_settings.us_unit_id= %s AND us_act_id=%s ''', (self.unit_id, setting_id))
        setting_type = libpg.query_one('select unit_set_form, unit_set_strings from unit_set_types where unit_set_id = %s', (setting_id,))
        if current_settting is None:
            """não tem este settings"""
            self.close()
            settings_form_parser(setting_id, title, setting_type[0], setting_type[1], data=None)
    
        else:
            if current_settting[1] is True:
                """ tem setting pode editar e permite mais de um"""
                self.close()
                settings_form_parser(setting_id, title, setting_type[0],setting_type[1], data=None)
            else:
                """ tem setting mas não é editavel"""
                QMessageBox.warning(None, "Erro",
                                    "Esta configuração já existe\n e não pode ser adicionada novamente!\nTem de ser editada!")


def settings_form_parser(set_id, title, frm_type, set_strings, data=None):
    if frm_type == 'STR2':
        form = classes_un.InputTwoString(set_id, title, set_strings, data)
        form.exec_()
    elif frm_type == 'STR1':
        form = classes_un.InputOneString(set_id, title, set_strings, data)
        form.exec_()
    elif frm_type == 'SP01':
        """DDNS"""
        form = ddns_edit.DdnsEdit(set_id , data[0], data[1])
        form.exec_()
    elif frm_type == 'SOFT':
        """software"""
        form = software.SoftwareBrowser(gl.unit_dict)
        form.exec_()
        if form.ret[0]:
            if data is None:
                liblogos.insert_unit_setting(gl.unit_dict['un_id'], 1, form.ret[1], form.ret[2])
            else:
                liblogos.update_unit_settings(set_id, form.ret[1], form.ret[2])
            liblogos.software_update_settings(gl.unit_dict['un_id'])
    elif frm_type == 'DATE':
        form = classes_un.InputDateSettings(set_id, title, set_strings, data)
        form.exec_()
        # á data de instalação adicionar um compromisso de alpha + 30 dias
        if form.ret[0]:
            liblogos.add_unit_comitment(gl.unit_dict['un_id'], 15, form.ret[1] + datetime.timedelta(days=30), 'auto', reset=True)

    elif frm_type == 'DB02':
        print('call DB02')
        form = classes_un.DbmsDialog(set_id, title, data)
        form.exec_()
    elif frm_type == 'DB01':
        form = classes_un.OsSetDialog(set_id,title, set_strings,data=data)
        form.exec_()
    elif frm_type == 'DB03':
        form = classes_un.SetArch(set_id,title, set_strings,data=data)
        form.exec_()


def settings_add_edit(unit_id, setting_id, unit_type,terminal_names):
    if setting_id == 1:
        form = software.SoftwareBrowser({'un_type': unit_type})
        form.exec_()
        if form.ret[0]:
            liblogos.insert_unit_setting(unit_id, 1, form.ret[1], form.ret[2])
            liblogos.software_update_settings(unit_id)
    elif setting_id == 2:
        form = classes_un.TerminalsDialog(unit_id, setting_id,edit=False)
        form.exec_()
    # elif setting_id == 3:
    #     form = classes_un.ProductionPrinters(unit_id, ptype=3, count=0, title='Adicionar Monitores de Pedidos', label_title='Monitores',edit=False)
    #     form.exec_()
    # elif setting_id == 5:
    #     form = classes_un.ProductionPrinters(edit=False, unit_id=unit_id, ptype=5,
    #                                          title='Adicionar Impressoras de Contas',
    #                                          label_title='Impressoras de Contas')
    #     form.exec_()
    # elif setting_id == 6:
    #     form = classes_un.ProductionPrinters(edit=False, unit_id=unit_id, ptype=6,
    #                                          title='Adicionar Impressoras de Pedidos',
    #                                          label_title='Impressoras de Pedidos')
    #     form.exec_()
    # elif setting_id == 7:
    #     form = classes_un.ProductionPrinters(edit=False, unit_id=unit_id, ptype=7, title='Adicionar Sessões RDP',
    #                                          label_title='Sessões RDP')
    #     form.exec_()
    elif setting_id == 8:
        form = classes_un.DbmsDialog(edit=False, unit_id=kwargs['unit_id'], act_id=kwargs['act_id'],
                                     unit_type=kwargs['unit_type'])
        form.exec_()
    elif setting_id == 9:
        form = classes_un.SetArch(edit=False, act_id=9, unit_id=kwargs['unit_id'], arch_type='Monoposto')
        form.exec_()
    elif setting_id == 10:
        form = classes_un.OsSetDialog(edit=False, act_id=10, unit_id=kwargs['unit_id'], version='Windows 7',
                                      arch='32 bit')
        form.exec_()
    elif setting_id == 11:
        form = classes_un.InputDateSettings(act_id=11, unit_id=unit_id, title='Data de Instalação', eternal=False,
                                            edit=False)
        form.exec_()
        # á data de instalação adicionar um compromisso de alpha + 30 dias
        if form.ret[0]:
            liblogos.add_unit_comitment(unit_id, 15, form.ret[1] + datetime.timedelta(days=30), 'auto', reset=True)
    # elif setting_id == 12:
    #     form = classes_un.SetIsp(unit_id=kwargs['unit_id'], edit=False, v1='NOS', v2='192.168.1.1')
    #     form.exec_()
    # elif setting_id == 13:
    #     form = ddns_edit.DdnsEdit(-1, '', '')
    #     form.exec_()
    # elif setting_id == 14:
    #     form = classes_un.SetText(act_id=setting_id, unit_id=unit_id, edit=False, field1='ID', field2='Obs',
    #                               title='TeamViewer', v1='Servidor ID', v2='Nome')
    #     form.exec_()
    # elif setting_id == 15:
    #     form = classes_un.SetText(act_id=setting_id, unit_id=unit_id, edit=False, field1='ID', field2='Posto',
    #                               title='TeamViewer Posto', v1='Posto ID', v2='Nome')
    #     form.exec_()
    # elif setting_id == 16:
    #     form = classes_un.SetText(act_id=setting_id, unit_id=unit_id, edit=False, field1='ID', field2='Obs',
    #                               title='AnyDesk', v1='Servidor ID', v2='Nome')
    #     form.exec_()
    # elif setting_id == 17:
    #     form = classes_un.SetText(act_id=setting_id, unit_id=unit_id, edit=False, field1='ID', field2='Posto',
    #                               title='AnyDesk Posto', v1='Posto ID', v2='Nome')
    #     form.exec_()
    elif setting_id == 19:
        form = classes_un.SetTextOne(act_id=setting_id, unit_id=unit_id, edit=False, field1='Password',
                                     title='Backoffice Password')
        form.exec_()
    elif setting_id == 20:
        form = classes_un.SetTextOne(act_id=setting_id, unit_id=unit_id, edit=False, field1='Série',
                                     title='Numero da Série')
        form.exec_()
    elif setting_id == 21:
        form = classes_un.SetTextOne(act_id=setting_id, unit_id=unit_id, edit=False, field1='Operador',
                                     title='Backoffice Operador')
        form.exec_()
    elif setting_id == 27:
        form = classes_un.SetText(act_id=setting_id, unit_id=unit_id, edit=False, field1='Utilizador',
                                  field2='Password', title='Utilizador/e-mail', v1='', v2='')
        form.exec_()


def edit_settings_main(**kwargs):
    """APAGAR """
    if kwargs is not None:
        # act_id = kwargs['act_id']
        if kwargs['act_id'] == 1:
            form = software.SoftwareBrowser({'unit_type': kwargs['unit_type']})
            form.exec_()
            if form.ret[0]:
                liblogos.update_unit_settings(kwargs['us_id'], form.ret[1], form.ret[2])
                liblogos.software_update_settings(kwargs['unit_id'])
        elif kwargs['act_id'] == 2:
            form = classes_un.TerminalsDialog(edit=True, us_id=kwargs['us_id'], names=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 8:
            form = classes_un.DbmsDialog(edit=True, us_id=kwargs['us_id'], unit_type=kwargs['unit_type'])
            form.exec_()
        elif kwargs['act_id'] == 9:
            form = classes_un.SetArch(us_id=kwargs['us_id'], edit=True, arch_type='Monoposto')
            form.exec_()
        elif kwargs['act_id'] == 10:
            form = classes_un.OsSetDialog(edit=True, us_id=kwargs['us_id'], unit_id=kwargs['unit_id'],
                                          version=kwargs['v1'], arch=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 5:
            form = classes_un.ProductionPrinters(us_id=kwargs['us_id'], edit=True, ptype=5,
                                                 title='Alterar Impressoras de Contas',
                                                 label_title='Impressoras de Contas',
                                                 count=kwargs['v1'], names=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 3:
            form = classes_un.ProductionPrinters(us_id=kwargs['us_id'], edit=True, ptype=3,
                                                 title='Adicionar Monitores de Pedidos', label_title='Monitores',
                                                 count=kwargs['v1'], names=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 6:
            form = classes_un.ProductionPrinters(us_id=kwargs['us_id'], edit=True, ptype=6,
                                                 title='Alterar Impressoras de Pedidos', label_title='Impressoras',
                                                 count=kwargs['v1'], names=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 7:
            form = classes_un.ProductionPrinters(us_id=kwargs['us_id'], edit=True, ptype=7,
                                                 title='Alterar Sessões RDP/iPads', label_title='Secções',
                                                 count=kwargs['v1'], names=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 12:
            form = classes_un.SetIsp(us_id=kwargs['us_id'], edit=True, v1=kwargs['v1'], v2=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 13:
            form = ddns_edit.DdnsEdit(kwargs['us_id'], kwargs['v1'], kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 14:
            form = classes_un.SetText(us_id=kwargs['us_id'], edit=True, title='TeamViewer ID', field1='Servidor ID',
                                      field2='Nome', v1=kwargs['v1'], v2=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 15:
            form = classes_un.SetText(us_id=kwargs['us_id'], edit=True, title='TeamViewer ID', field1='Posto ID',
                                      field2='Nome', v1=kwargs['v1'], v2=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 16:
            form = classes_un.SetText(us_id=kwargs['us_id'], edit=True, title='AnyDesk ID', field1='Servidor ID',
                                      field2='Nome', v1=kwargs['v1'], v2=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 19:
            form = classes_un.SetTextOne(us_id=kwargs['us_id'], edit=True, field1='Password',
                                         title='Backoffice Password', v1=kwargs['v1'])
            form.exec_()
        elif kwargs['act_id'] == 20:
            form = classes_un.SetTextOne(us_id=kwargs['us_id'], edit=True, field1='Série', title='Numero da Série',
                                         v1=kwargs['v1'])
            form.exec_()
        elif kwargs['act_id'] == 21:
            form = classes_un.SetTextOne(us_id=kwargs['us_id'], edit=True, field1='Operador',
                                         title='Backoffice Operador', v1=kwargs['v1'])
            form.exec_()
        elif kwargs['act_id'] == 22:
            form = classes_un.SetTextOne(us_id=kwargs['us_id'], edit=True, field1='Código de Autorização',
                                         title='Código IWS', v1=kwargs['v1'])
            form.exec_()
        elif kwargs['act_id'] == 27:
            form = classes_un.SetText(us_id=kwargs['us_id'], edit=True, title='Credenciais', field1='Utilizador',
                                      field2='Password', v1=kwargs['v1'], v2=kwargs['v2'])
            form.exec_()


if __name__ == '__main__':
    pass