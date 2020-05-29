#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout, QPushButton, QTableWidget, QHBoxLayout, QComboBox, \
    QCheckBox

import date_input
import ex_grid
import libpg
import models
import qlib as qc
import report_display
import report_lib
import software
import unit


class ReportTool(QDialog):
    def __init__(self, rep_type, parent=None):
        super(ReportTool, self).__init__(parent)
        self.setWindowTitle('Relatórios')
        self.resize(1024, 768)
        self.rep_type = rep_type
        self.ret = {'status': False}
        masterLayout = QVBoxLayout(self)
        buttonLayout = QHBoxLayout()
        self.updateBtn = QPushButton('Actualiza')
        self.updateBtn.clicked.connect(self.update_click)
        self.printBtn = QPushButton('Print')
        self.printBtn.clicked.connect(self.print_report)
        
        
        cancelBtn = QPushButton('Sair')
        cancelBtn.clicked.connect(self.exit)
        buttonLayout.addWidget(cancelBtn)
        self.reportTypeCbx = QComboBox()
        # self.reportTypeCbx.currentIndexChanged.connect(self.report_change)
        self.unitActiveCkBox = QCheckBox('Activas')
        self.unitActiveCkBox.setChecked(True)
        masterLayout.addLayout(
            qc.addHLayout([self.reportTypeCbx, self.updateBtn, self.printBtn, True, self.unitActiveCkBox, True, cancelBtn]))
        
        self.gridMain = QTableWidget()
        self.gridMain.itemDoubleClicked.connect(self.grid_click)
        self.gridMain.setSelectionBehavior(QTableWidget.SelectRows)
        self.gridMain.setSelectionMode(QTableWidget.SingleSelection)
        self.gridMain.setEditTriggers(QTableWidget.NoEditTriggers)
        self.gridMain.verticalHeader().setDefaultSectionSize(20)
        self.gridMain.setAlternatingRowColors(True)
        self.gridMain.setStyleSheet("alternate-background-color: #f5f5f0;")
        self.gridMain.verticalHeader().setVisible(False)
        
        masterLayout.addWidget(self.gridMain)
        self.update_report_type()
    
    def update_report_type(self):
        hl = libpg.sql_query(
            'SELECT report_name FROM reports WHERE report_group=\'' + self.rep_type + '\' and report_visible=True order by report_order')
        self.reportTypeCbx.addItem('')
        for n in hl:
            rep = n[0]
            self.reportTypeCbx.addItem(rep)
    
    def update_click(self):
        report: str = self.reportTypeCbx.currentText().lower()
        if report == 'unidades com modelo':
            form = models.ModelsBrowser({'mode': 1})
            form.exec_()
            form.ret['model_id'] = form.ret.get('model_id', 0)
            if form.ret['model_id'] > 0:
                sql = '''SELECT  un_id, un_nome, un_localidade, un_cp
                     FROM unidades
                     inner join hardware on unidades.un_id=hardware.hw_unit_id
                      where  hardware.hw_model_id=%s'''
                sql += ''' ORDER BY un_nome'''
                bc = libpg.query_many(sql, (form.ret['model_id'],))
                ex_grid.make_grid(self.gridMain, ['ID', 'Unidade', 'Localidade', 'Código Postal'],
                                  [(0, 50), (1, 320), (2, 200), (3, 260)])
                ex_grid.grid_std(self.gridMain, data=bc, f_col=['i', 's', 's', 's'])
                self.setWindowTitle(self.reportTypeCbx.currentText())
        elif report == 'versão do software':
            """unidades por softwate"""
            form = software.SoftwareBrowser({'un_type': 0})
            form.exec_()
            if form.ret[0]:
                sql = ''' SELECT  un_id, un_nome, un_localidade, un_cp, area_name
                     FROM unit_settings
                     inner join unidades on unidades.un_id = unit_settings.us_unit_id
                     inner join areas  on areas.area_id = unidades.un_area
                     where unit_settings.us_act_id=1 and lower(us_value1) = %s and lower(us_value2) = %s and  unidades.un_activa = %s'''
                sql += ''' ORDER BY un_nome '''
                xl = libpg.query_many(sql,
                                      (form.ret[1].lower(), form.ret[2].lower(), str(self.unitActiveCkBox.isChecked())))
                ex_grid.make_grid(self.gridMain, ['ID', 'Unidade', 'Localidade', 'Código Postal', 'Zona'],
                                  [(0, 50), (1, 320), (2, 260), (3, 260), (4, 260)])
                ex_grid.grid_std(self.gridMain, data=xl, f_col=['i', 's', 's', 's', 's'])
                
                self.setWindowTitle(self.reportTypeCbx.currentText() + ' ' + form.ret[1] + ':' + form.ret[2])
        elif report == 'call center a terminar':
            form = date_input.DateInput(report.upper())
            form.exec_()
            if form.ret[0]:
                sql = '''SELECT cm_unit_id, unidades.un_nome,un_localidade,
                          comitments_unit.cm_value,(to_date(comitments_unit.cm_value, 'YYYY-MM-DD') - DATE 'now') as s,
                          areas.area_name
                         FROM comitments_unit
                         inner join unidades on unidades.un_id= comitments_unit.cm_unit_id
                         inner join areas on unidades.un_area= area_id
                         WHERE  comitments_unit.cm_act_id=15 and cm_archive = False
                         and (to_date(comitments_unit.cm_value, 'YYYY-MM-DD') >= %s
                         and to_date(comitments_unit.cm_value, 'YYYY-MM-DD') <= %s)
                         and  un_activa=True
                         order by s asc'''
                xl = libpg.query_many(sql, (form.ret[1], form.ret[2]))
                ex_grid.make_grid(self.gridMain, ['ID', 'Unidade', 'Localidade', 'Data', 'Dias', 'Zona'],
                                  [(0, 50), (1, 320), (2, 240), (3, 100), (4, 30), (5, 260)])
                ex_grid.grid_std(self.gridMain, data=xl, f_col=['i', 's', 's', 's', 'i', 's'])
                self.setWindowTitle(self.reportTypeCbx.currentText() + ' de' + form.ret[1] + ' a ' + form.ret[2])
        elif report == 'software a terminar':  # validade da licença
            form = date_input.DateInput(report.upper())
            form.exec_()
            if form.ret[0]:
                sql = '''SELECT cm_unit_id, unidades.un_nome,un_localidade,
                          comitments_unit.cm_value,(to_date(comitments_unit.cm_value, 'YYYY-MM-DD') - DATE 'now') as s,
                          areas.area_name
                         FROM comitments_unit
                         inner join unidades on unidades.un_id= comitments_unit.cm_unit_id
                         inner join areas on unidades.un_area= area_id
                         WHERE  comitments_unit.cm_act_id=14 and cm_archive = False
                         and (to_date(comitments_unit.cm_value, 'YYYY-MM-DD') >= %s
                         and to_date(comitments_unit.cm_value, 'YYYY-MM-DD') <= %s)
                         and  un_activa=True
                         order by s asc'''
                xl = libpg.query_many(sql, (form.ret[1], form.ret[2]))
                ex_grid.make_grid(self.gridMain, ['ID', 'Unidade', 'Localidade', 'Data', 'Dias', 'Zona'],
                                  [(0, 50), (1, 320), (2, 240), (3, 100), (4, 30), (5, 260)])
                ex_grid.grid_std(self.gridMain, data=xl, f_col=['i', 's', 's', 's', 'i', 's'])
                self.setWindowTitle(self.reportTypeCbx.currentText() + ' de' + form.ret[1] + ' a ' + form.ret[2])
        elif report == 'eorder a terminar':  # eorder
            form = date_input.DateInput(report.upper())
            form.exec_()
            if form.ret[0]:
                sql = '''SELECT cm_unit_id, unidades.un_nome,un_localidade,
                          comitments_unit.cm_value,(to_date(comitments_unit.cm_value, 'YYYY-MM-DD') - DATE 'now') as s,
                          areas.area_name
                         FROM comitments_unit
                         inner join unidades on unidades.un_id= comitments_unit.cm_unit_id
                         inner join areas on unidades.un_area= area_id
                         WHERE  comitments_unit.cm_act_id=24 and cm_archive = False
                         and (to_date(comitments_unit.cm_value, 'YYYY-MM-DD') >= %s
                         and to_date(comitments_unit.cm_value, 'YYYY-MM-DD') <= %s)
                         and  un_activa=True
                         order by s asc'''
                xl = libpg.query_many(sql, (form.ret[1], form.ret[2]))
                ex_grid.make_grid(self.gridMain, ['ID', 'Unidade', 'Localidade', 'Data', 'Dias', 'Zona'],
                                  [(0, 50), (1, 320), (2, 240), (3, 100), (4, 30), (5, 260)])
                ex_grid.grid_std(self.gridMain, data=xl, f_col=['i', 's', 's', 's', 'i', 's'])
                self.setWindowTitle(self.reportTypeCbx.currentText() + ' de' + form.ret[1] + ' a ' + form.ret[2])
        elif report == 'software a bloqueiar':  # software a Bloqueiar chave=13
            form = date_input.DateInput(report.upper())
            form.exec_()
            if form.ret[0]:
                sql = '''SELECT cm_unit_id, unidades.un_nome,un_localidade,
                          comitments_unit.cm_value,
                          (to_date(comitments_unit.cm_value, 'YYYY-MM-DD') - DATE 'now') as s, 'Zona'
                         FROM comitments_unit,unidades
                         WHERE  comitments_unit.cm_act_id=13 and cm_archive = False
                         and (to_date(comitments_unit.cm_value, 'YYYY-MM-DD') >= %s
                         and to_date(comitments_unit.cm_value, 'YYYY-MM-DD') <= %s)
                         and unidades.un_id= comitments_unit.cm_unit_id and un_activa=True
                         order by s asc'''
                xl = libpg.query_many(sql, (form.ret[1], form.ret[2]))
                ex_grid.make_grid(self.gridMain, ['ID', 'Unidade', 'Localidade', 'Data',' Dias', 'Zona'],
                                  [(0, 50), (1, 260), (2, 180), (3, 100), (4, 40), (5,260)])
                ex_grid.grid_std(self.gridMain, data=xl, f_col=['i', 's', 's', 's', 'i','s'])
                self.setWindowTitle(self.reportTypeCbx.currentText() + ' de' + form.ret[1] + ' a ' + form.ret[2])
        elif report == 'licenças pedidas':
            sql = '''SELECT  software.sf_id, un_nome, software_lic_status.lic_st_name,
                 to_char(software.sf_time_order, 'YYYY-MM-DD HH24:MI') as orde,area_name,
                to_char(date 'now' - sf_time_order, 'DD" dias "HH24" horas'), lic_st_id,un_id
                 FROM software
                 inner join software_type  on software.sf_version = software_type.sft_id
                 inner join software_lic_status on lic_st_id=sf_status
                 inner join unidades on un_id=sf_unit_id
                 inner join areas on un_area=areas.area_id
                    WHERE lic_st_id=0
                 ORDER BY software.sf_id DESC, sf_date_valid DESC;'''
            xl = libpg.query_many(sql, (True,))
            ex_grid.make_grid(self.gridMain, ['ID', 'Unidade', 'Estado', 'Data', 'Zona', 'Atraso','st_lic','unit_id'],
                              [(0, 50), (1, 240), (2, 80), (3, 140), (4, 260), (5, 120),(6,0), (7,0)])
            ex_grid.grid_std(self.gridMain, data=xl, f_col=['i', 's', 's', 's', 's','s', 'i','i'])
            self.setWindowTitle(self.reportTypeCbx.currentText())
        elif report == 'unidades em actualização':
            sql = '''SELECT  software.sf_id, un_nome, software_lic_status.lic_st_name,
                 to_char(software.sf_time_order, 'YYYY-MM-DD HH24:MI') as orde,area_name,
                to_char(date 'now' - sf_time_order, 'DD" dias "HH24" horas'), lic_st_id,unidades.un_id
                 FROM software
                 inner join software_type  on software.sf_version = software_type.sft_id
                 inner join software_lic_status on lic_st_id=sf_status
                 inner join unidades on un_id=sf_unit_id
                 inner join areas on un_area=areas.area_id
                    WHERE lic_st_id=3
                 ORDER BY software.sf_id DESC, sf_date_valid DESC;'''
            xl = libpg.query_many(sql, (True,))
            ex_grid.make_grid(self.gridMain, ['ID', 'Unidade', 'Estado', 'Data', 'Zona', 'Atraso','st_lic','unit_id'],
                              [(0, 50), (1, 240), (2, 120), (3, 140), (4, 260), (5, 120),(6,0),(7,0)])
            ex_grid.grid_std(self.gridMain, data=xl, f_col=['i', 's', 's', 's', 's','s', 'i','i'])
            self.setWindowTitle(self.reportTypeCbx.currentText())
        elif report == 'unidades actualizadas':
            sql = '''SELECT  software.sf_id, un_nome, software_lic_status.lic_st_name,
                 to_char(software.sf_time_order, 'YYYY-MM-DD HH24:MI') as orde,area_name,
                to_char(date 'now' - sf_time_order, 'DD" dias "HH24" horas'), lic_st_id,unidades.un_id
                 FROM software
                 inner join software_type  on software.sf_version = software_type.sft_id
                 inner join software_lic_status on lic_st_id=sf_status
                 inner join unidades on un_id=sf_unit_id
                 inner join areas on un_area=areas.area_id
                    WHERE lic_st_id=4  and (sf_time_order between NOW() - INTERVAL '30 DAY' and 'now')
                 ORDER BY sf_time_order DESC;'''
            xl = libpg.query_many(sql, (True,))
            ex_grid.make_grid(self.gridMain, ['ID', 'Unidade', 'Estado', 'Data', 'Zona', 'Atraso','st_lic','unit_id'],
                              [(0, 50), (1, 240), (2, 120), (3, 140), (4, 260), (5, 120),(6,0),(7,0)])
            ex_grid.grid_std(self.gridMain, data=xl, f_col=['i', 's', 's', 's', 's','s', 'i','i'])
            self.setWindowTitle(self.reportTypeCbx.currentText())
        
        
    def grid_click(self):
        try:
            self.ret['unit_id'] = int(self.gridMain.item(self.gridMain.currentRow(), 7).text())
            self.ret['status'] = True
            # if form.ret['status']:
            form = unit.UnitEdit(self.ret['unit_id'])
            form.exec_()

        except AttributeError:
            # self.ret['status'] = False
            pass
    
    def grid_refresh(self):
        hl = [(1, 1, 'a', 'b', 'c', 'd', 99,00)]
        ex_grid.grid_std(self.gridMain, data=hl, f_col=['i', 'i', 's', 's', 's', 's', 'i','i'])

    def print_report(self):
        data_set = []
        for linha in range(0, self.gridMain.rowCount()):
            # proc_html = proc_html + self.grid_units.item(linha,0).text() +  self.grid_units.item(linha,1).text() + self.grid_units.item(linha,3).text() + self.grid_units.item(linha,4).text() + '<br>'
            dum = (self.gridMain.item(linha, 0).text(),)
            for col in range(1, self.gridMain.columnCount()):
                dum = dum + (self.gridMain.item(linha, col).text(),)
            data_set.append(dum)
    
        header = []
        for n in range(0, self.gridMain.columnCount()):
            header.append(self.gridMain.horizontalHeaderItem(n).text())
        proc_html = report_lib.unit_grid_report(data_set, header)
        form = report_display.DisplayReport(proc_html)
        form.exec_()
        
    def exit(self):
        self.close()


def main():
    app = QApplication(sys.argv)
    form = ReportTool('LIC')
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
