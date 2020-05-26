#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from PyQt5.QtWidgets import QInputDialog, QLineEdit

import parameters as gl
import classes_un
import liblogos
import libpg
import ddns_edit
import software


def edit_contact_main(ct_id, unit_id, title, v1, v2, way):
    pass

def add_settings_main(**kwargs):
    if kwargs is not None:
        unit_id = kwargs['unit_id']
        act_id = kwargs['act_id']
        if act_id == 1:
            form = software.SoftwareBrowser({'unit_type': kwargs['unit_type']})
            form.exec_()
            if form.ret[0]:
                liblogos.insert_unit_setting(unit_id, 1, form.ret[1], form.ret[2])
                liblogos.software_update_settings(unit_id)
        elif act_id == 2:
            form = classes_un.TerminalsDialog(edit=False, unit_id=kwargs['unit_id'], act_id=kwargs['act_id'])
            form.exec_()
        elif act_id == 3:
            form = classes_un.ProductionPrinters(edit=False, unit_id=unit_id, ptype=3, title='Adicionar Monitores de Pedidos', label_title='Monitores')
            form.exec_()
        elif act_id == 5:
            form = classes_un.ProductionPrinters(edit=False, unit_id=unit_id, ptype=5, title='Adicionar Impressoras de Contas', label_title='Impressoras de Contas')
            form.exec_()
        elif act_id == 6:
            form = classes_un.ProductionPrinters(edit=False, unit_id=unit_id, ptype=6, title='Adicionar Impressoras de Pedidos', label_title='Impressoras de Pedidos')
            form.exec_()
        elif act_id == 7:
            form = classes_un.ProductionPrinters(edit=False, unit_id=unit_id, ptype=7, title='Adicionar Sessões RDP', label_title='Sessões RDP')
            form.exec_()
        elif act_id == 8:
            form = classes_un.DbmsDialog(edit=False, unit_id=kwargs['unit_id'], act_id=kwargs['act_id'], unit_type=kwargs['unit_type'])
            form.exec_()
        elif act_id == 9:
            form = classes_un.SetArch(edit=False, act_id=9, unit_id=kwargs['unit_id'] , arch_type= 'Monoposto' )
            form.exec_()
        elif act_id == 10:
            form = classes_un.OsSetDialog(edit=False, act_id=10, unit_id=kwargs['unit_id'], version='Windows 7', arch='32 bit' )
            form.exec_()
        elif act_id == 11:
            form = classes_un.InputDateSettings(act_id=11, unit_id=unit_id, title='Data de Instalação', eternal=False, edit=False)
            form.exec_()
            # á data de instalação adicionar um compromisso de alpha + 30 dias
            if form.ret[0]:
                liblogos.add_unit_comitment(unit_id, 15, form.ret[1] + datetime.timedelta(days=30), 'auto', reset=True)
        elif act_id == 12:
            form = classes_un.SetIsp(unit_id=kwargs['unit_id'], edit=False, v1='NOS', v2='192.168.1.1')
            form.exec_()
        elif act_id == 13:
            form = ddns_edit.DdnsEdit(-1,'','')
            form.exec_()
        elif act_id == 14:
            form = classes_un.SetText(act_id=act_id, unit_id=unit_id, edit=False, field1='ID',field2='Obs', title='TeamViewer', v1='Servidor ID', v2='Nome' )
            form.exec_()
        elif act_id == 15:
            form = classes_un.SetText(act_id=act_id, unit_id=unit_id, edit=False, field1='ID',field2='Posto', title='TeamViewer Posto', v1= 'Posto ID', v2='Nome' )
            form.exec_()
        elif act_id == 16:
            form = classes_un.SetText(act_id=act_id, unit_id=unit_id, edit=False, field1='ID',field2='Obs', title='AnyDesk', v1='Servidor ID', v2='Nome' )
            form.exec_()
        elif act_id == 17:
            form = classes_un.SetText(act_id=act_id, unit_id=unit_id, edit=False, field1='ID',field2='Posto', title='AnyDesk Posto', v1= 'Posto ID', v2='Nome' )
            form.exec_()
        elif act_id == 19:
            form = classes_un.SetTextOne(act_id=act_id, unit_id=unit_id, edit=False, field1='Password', title='Backoffice Password')
            form.exec_()
        elif act_id == 20:
            form = classes_un.SetTextOne(act_id=act_id, unit_id=unit_id, edit=False, field1='Série', title='Numero da Série')
            form.exec_()
        elif act_id == 21:
            form = classes_un.SetTextOne(act_id=act_id, unit_id=unit_id, edit=False, field1='Operador', title='Backoffice Operador')
            form.exec_()
        elif act_id == 27:
            form = classes_un.SetText(act_id=act_id, unit_id=unit_id, edit=False, field1='Utilizador',field2='Password', title='Utilizador/e-mail',v1='', v2='')
            form.exec_()


def edit_settings_main(**kwargs):
    if kwargs is not None:
        # act_id = kwargs['act_id']
        if kwargs['act_id'] == 1:
            form = software.SoftwareBrowser({'unit_type': kwargs['unit_type']})
            form.exec_()
            if form.ret[0]:
                liblogos.update_unit_settings(kwargs['us_id'], form.ret[1], form.ret[2])
                liblogos.software_update_settings(kwargs['unit_id'])
        elif kwargs['act_id'] == 2:
            form = classes_un.TerminalsDialog(edit=True, us_id=kwargs['us_id'],names=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 8:
            form = classes_un.DbmsDialog(edit=True, us_id=kwargs['us_id'], unit_type=kwargs['unit_type'])
            form.exec_()
        elif kwargs['act_id'] == 9:
            form = classes_un.SetArch(us_id=kwargs['us_id'], edit=True, arch_type= 'Monoposto')
            form.exec_()
        elif kwargs['act_id'] == 10:
            form = classes_un.OsSetDialog(edit=True, us_id=kwargs['us_id'], unit_id=kwargs['unit_id'], version=kwargs['v1'], arch=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 5:
            form = classes_un.ProductionPrinters(us_id=kwargs['us_id'], edit=True,  ptype=5, title='Alterar Impressoras de Contas', label_title='Impressoras de Contas',
                                                 count=kwargs['v1'], names=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 3:
            form = classes_un.ProductionPrinters(us_id=kwargs['us_id'], edit=True, ptype=3, title='Adicionar Monitores de Pedidos', label_title='Monitores',
                                                 count=kwargs['v1'], names=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 6:
            form = classes_un.ProductionPrinters(us_id=kwargs['us_id'], edit=True, ptype=6, title='Alterar Impressoras de Pedidos', label_title='Impressoras',
                                                 count=kwargs['v1'], names=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 7:
            form = classes_un.ProductionPrinters(us_id=kwargs['us_id'], edit=True, ptype=7, title='Alterar Sessões RDP/iPads', label_title='Secções',
                                                 count=kwargs['v1'], names=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 12:
            form = classes_un.SetIsp(us_id=kwargs['us_id'], edit=True, v1=kwargs['v1'], v2=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 13:
            form = ddns_edit.DdnsEdit(kwargs['us_id'], kwargs['v1'], kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 14:
            form = classes_un.SetText(us_id=kwargs['us_id'], edit=True, title='TeamViewer ID', field1='Servidor ID', field2='Nome', v1=kwargs['v1'], v2=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 15:
            form = classes_un.SetText(us_id=kwargs['us_id'], edit=True, title='TeamViewer ID', field1='Posto ID', field2='Nome', v1=kwargs['v1'], v2=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 16:
            form = classes_un.SetText(us_id=kwargs['us_id'], edit=True, title='AnyDesk ID', field1='Servidor ID', field2='Nome', v1=kwargs['v1'], v2=kwargs['v2'])
            form.exec_()
        elif kwargs['act_id'] == 19:
            form = classes_un.SetTextOne(us_id=kwargs['us_id'], edit=True, field1='Password', title='Backoffice Password',v1=kwargs['v1'])
            form.exec_()
        elif kwargs['act_id']  == 20:
            form = classes_un.SetTextOne(us_id=kwargs['us_id'], edit=True, field1='Série', title='Numero da Série',v1=kwargs['v1'])
            form.exec_()
        elif kwargs['act_id']  == 21:
            form = classes_un.SetTextOne(us_id=kwargs['us_id'], edit=True, field1='Operador', title='Backoffice Operador',v1=kwargs['v1'])
            form.exec_()
        elif kwargs['act_id'] == 22:
            form = classes_un.SetTextOne(us_id=kwargs['us_id'], edit=True, field1='Código de Autorização', title='Código IWS',v1=kwargs['v1'])
            form.exec_()
        elif kwargs['act_id'] == 27:
            form = classes_un.SetText(us_id=kwargs['us_id'], edit=True, title='Credenciais', field1='Utilizador', field2='Password', v1=kwargs['v1'], v2=kwargs['v2'])
            form.exec_()

if __name__ == '__main__':
    pass