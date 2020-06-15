#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import json
import pprint
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QLineEdit, QTabWidget, QPushButton, \
    QWidget, QToolButton, QDateEdit, QPlainTextEdit, QMessageBox, QErrorMessage, QDesktopWidget, QComboBox, QTableWidget
from dateutil.relativedelta import relativedelta

import cp
import data_sets
import ex_grid
import insoft_c_version
import liblogos
import libpg
import parameters as gl
import qlib
import qlib as qc
import smtpmail
import stdio


class MakeLic(QDialog):
    def __init__(self, unit_id,lic_id, parent=None):
        super(MakeLic,  self).__init__(parent)
        self.com_version_data = None
        self.resize(800, 800)
        """ entra: unidade, lic_id na tabela software"""
        masterLayout = QVBoxLayout(self)
        self.center()
        self.unit_id = unit_id
        self.lic_id = lic_id
        self.unit_dict = {}
        self.client_dict = {}
        self.lic_values = {}
        self.get_db_data()
        self.last_lic_dict = {}
        self.software_id = 0
        # self.comercial_version_key = ''
        if self.lic_id == -1:
            self.lic_values['lic_type'] = 1
            self.lic_values['lictype_txt'] = 'Nova'
        else:
            self.lic_values['lictype_txt'] = 'Actualização'
            self.lic_values['lic_type'] = 2
        """ make tabs """
        self.tabuladorTabWidget = QTabWidget()
        self.make_order_tab()
        self.tabuladorTabWidget.addTab(self.tab1, 'Licença')
        self.make_client_tab()
        self.tabuladorTabWidget.addTab(self.tab2, 'Sede Social')
        self.make_comments_tab()
        self.tabuladorTabWidget.addTab(self.tab3, 'Comentarios')
        masterLayout.addWidget(self.tabuladorTabWidget)
        make_Btn = QPushButton('Gera Lic')
        make_Btn.setDefault(False)
        make_Btn.setAutoDefault(False)
        make_Btn.clicked.connect(self.make_lic_click)
    
        exitBtn = QPushButton('Sair')
        exitBtn.setDefault(False)
        exitBtn.setAutoDefault(False)
        exitBtn.clicked.connect(self.exit_click)
        masterLayout.addLayout(qc.addHLayout([make_Btn,exitBtn]))
        if self.lic_id == -1:
            self.refresh_form()
        else:
            self.renew_lic()
        self.setWindowTitle(self.lic_values['lictype_txt'] + ' licença.')

    def make_order_tab(self):
        self.tab1 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab1)
        tabLayout = QVBoxLayout()
        self.header = QLineEdit()
        self.header.setMaxLength(42)
        self.header.textChanged.connect(self.calc_len)
        self.hcounter = QLabel()
        self.hcounter.setMaximumWidth(20)
        self.hcounter.setMinimumWidth(20)
        self.phones = QLineEdit()
        self.phones.setMaxLength(9)
        self.phones.setInputMask('000000000')
        self.phones.setMaximumWidth(90)
        self.pcounter = QLabel()
        self.pcounter.setMaximumWidth(20)
        self.pcounter.setMinimumWidth(20)
        tabLayout.addLayout(qc.addHLayout(['Cabeçalho',self.header, self.hcounter,'Telefones',self.phones], lw=100))
        self.un_morada = QLineEdit()
        self.un_morada.setReadOnly(True)
        self.un_morada.setMaxLength(255)
        self.un_morada.setMaximumWidth(300)
        tabLayout.addLayout(qlib.addHLayout(['Morada', self.un_morada, True], lw=100))
        self.un_localidade = QLineEdit()
        self.un_localidade.setReadOnly(True)
        self.un_localidade.setMaxLength(35)
        self.un_localidade.setMaximumWidth(300)
        self.un_cp = QLineEdit()
        self.un_cp.setReadOnly(True)
        # self.un_cp.setMaximumWidth(300)
        cp_drill = QToolButton()
        cp_drill.setIcon(QIcon('.//img//drill_down.png'))
        cp_drill.setToolTip('Consultar Cliente')
        cp_drill.clicked.connect(self.cp_drill_down)
        tabLayout.addLayout(qlib.addHLayout(['Localidade', self.un_localidade,'Código Postal', self.un_cp,cp_drill], lw=100))
        tabLayout.addWidget(qc.HLine())
        self.date_contract = QDateEdit()
        self.date_contract.setMaximumWidth(140)
        self.date_contract.setMinimumWidth(140)
        self.date_contract.setDisplayFormat("yyyy-MM-dd")
        self.date_contract.setCalendarPopup(True)
        self.date_contract.setReadOnly(False)
        self.date_contract.dateChanged.connect(self.calc_date_end)
        
        self.date_valid = QDateEdit()
        self.date_valid.setMaximumWidth(140)
        self.date_valid.setMinimumWidth(140)
        self.date_valid.setDisplayFormat("yyyy-MM-dd")
        self.date_valid.setDate(datetime.datetime.now())
        self.date_valid.setCalendarPopup(True)

        self.software_type = QComboBox()
        self.software_type.setMinimumWidth(140)
        self.software_type.setEditable(True)
        self.software_type.addItems(self.get_software())
        self.software_version = QLabel(get_software_last_version())
        self.comercialVersionEdt = QLineEdit()
        comercialVersionDrill = QToolButton()
        comercialVersionDrill.setToolTip('Escolhe Versão Comercial')
        comercialVersionDrill.clicked.connect(self.com_version_drill)
        tabLayout.addLayout(qlib.addHLayout(['Data Cat.', self.date_contract,'Validade',self.date_valid,True]))
        tabLayout.addLayout(qlib.addHLayout(['Software',self.software_type,'V. Comercial', self.comercialVersionEdt, comercialVersionDrill,  True])) #  Versão,self.software,software_drill, True],lw=70))
        # grelha com as opções
        self.gridOptions = QTableWidget()
        self.gridOptions.setEditTriggers(QTableWidget.AnyKeyPressed)
        self.gridOptions.verticalHeader().setDefaultSectionSize(20)
        self.gridOptions.setAlternatingRowColors(True)
        self.gridOptions.setStyleSheet("alternate-background-color: #ffff99;")
        self.gridOptions.verticalHeader().setVisible(False)
        self.gridOptions.resizeColumnsToContents()
        ex_grid.make_grid(self.gridOptions, headers=['ID', 'Valor', 'Modulo', 'Preço', 'D'], col_width=[(0, 0), (1, 50), (2, 350), (3, 100), (4, 0)])
        if self.lic_values['lic_type'] == 1:  # nova
            bc = libpg.query_many('SELECT insoft_opt_code, null as qtd, insoft_opt_name, insoft_opt_price_1/100 FROM insoft_opt where insoft_opt_active = True and  insoft_opt_level = 2 ORDER BY insoft_opt_order')
        elif self.lic_values['lic_type'] == 2:  # renova
            bc = libpg.query_many('SELECT insoft_opt_code, null as qtd, insoft_opt_name, insoft_opt_price_2/100 FROM insoft_opt where insoft_opt_active = True and insoft_opt_level = 2 ORDER BY insoft_opt_order')
        ex_grid.grid_std(self.gridOptions, data=bc, f_col=['s', 's', 's', 'd2'])
        tabLayout.addWidget(self.gridOptions)
        self.gridOptions.cellChanged.connect(self.grid_change)

        self.total_public = QLineEdit()
        self.total_public.setMaximumWidth(60)
        self.total_public.setMinimumWidth(60)
        self.total_public.setAlignment(Qt.AlignVCenter|Qt.AlignRight)
        setPricesZeroBtn = QPushButton('0.00')
        setPricesZeroBtn.setFocusPolicy(Qt.NoFocus)
        setPricesZeroBtn.clicked.connect(self.set_prices_zero_click)

        tabLayout.addLayout(qc.addHLayout(['PVP', self.total_public, True,setPricesZeroBtn], label_align=Qt.AlignVCenter|Qt.AlignRight))

        mainTabLayout.addLayout(tabLayout)

    def make_client_tab(self):
        self.tab2 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab2)
        tabLayout = QVBoxLayout()

        self.cl_id = QLineEdit()
        self.cl_id.setMaxLength(4)
        self.cl_id.setMaximumWidth(100)
        self.cl_id.setReadOnly(True)
        self.cl_id.setStyleSheet("background-color: #dbf3ff;")
        tabLayout.addLayout(qlib.addHLayout(['#',self.cl_id, True], lw=120))

        self.cl_nif = QLineEdit()
        self.cl_nif.setReadOnly(True)
        self.cl_nif.setMaxLength(9)
        self.cl_nif.setMaximumWidth(100)
        tabLayout.addLayout(qlib.addHLayout(['NIF', self.cl_nif, True], lw=120))

        self.cl_nome = QLineEdit()
        self.cl_nome.setMaxLength(50)
        self.cl_nome.setMaximumWidth(300)
        tabLayout.addLayout(qlib.addHLayout(['D. Social', self.cl_nome, True], lw=120))
        self.cl_morada = QLineEdit()
        self.cl_morada.setReadOnly(True)
        self.cl_morada.setMaxLength(255)
        self.cl_morada.setMaximumWidth(300)
        tabLayout.addLayout(qlib.addHLayout(['Morada', self.cl_morada, True], lw=120))

        self.cl_localidade = QLineEdit()
        self.cl_localidade.setReadOnly(True)
        self.cl_localidade.setMaxLength(35)
        self.cl_localidade.setMaximumWidth(300)
        tabLayout.addLayout(qlib.addHLayout(['Localidade', self.cl_localidade, True], lw=120))

        self.cl_cap_social = QLineEdit()
        self.cl_cap_social.setReadOnly(True)
        self.cl_cap_social.setMaxLength(15)
        self.cl_cap_social.setAlignment(Qt.AlignRight)
        self.cl_cap_social.setMaximumWidth(100)
        self.cl_cap_social.setInputMask('0000000')
        tabLayout.addLayout(qlib.addHLayout(['Cap. Social', self.cl_cap_social, True], lw=120))

        self.cl_conservatoria = QLineEdit()
        self.cl_conservatoria.setReadOnly(True)
        self.cl_conservatoria.setMaxLength(100)
        self.cl_conservatoria.setMaximumWidth(300)
        tabLayout.addLayout(qlib.addHLayout(['Conservatória', self.cl_conservatoria, True], lw=120))

        self.cl_cp = QLineEdit()
        self.cl_cp.setReadOnly(True)
        self.cl_cp.setMaximumWidth(300)
        tabLayout.addLayout(qlib.addHLayout(['Código Postal', self.cl_cp, True], lw=120))
        self.cl_email = QLineEdit()
        self.cl_email.setReadOnly(True)
        self.cl_email.setMaxLength(30)
        self.cl_email.setMaximumWidth(300)
        tabLayout.addLayout(qlib.addHLayout(['e-mail', self.cl_email, True], lw=120))
        tabLayout.addStretch()
        mainTabLayout.addLayout(tabLayout)

    def make_comments_tab(self):
        self.tab3 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab3)
        tabLayout = QVBoxLayout()
        self.comments_Text = QPlainTextEdit()
        tabLayout.addWidget(self.comments_Text)
        label = QLabel()
        label.setStyleSheet("QLabel { background-color : white; color : blue; }")
        label.setText('Utilizar mudança de linha, mais conhecido como ENTER, nos comentários S.F.F.')
        tabLayout.addWidget(label)
        mainTabLayout.addLayout(tabLayout)
    
    def com_version_drill(self):
        form = insoft_c_version.ChangeComercialVersion()
        form.exec_()
        if form.ret[0]:
            self.com_version_data = form.ret
            self.comercialVersionEdt.setText(form.ret[2])
            self.com_version_data = data_sets.get_comercial_version(form.ret[1])
            self.grid_change()
            include_list = self.com_version_data['insoft_opt_include'].split(',')
            for linha in range(0, self.gridOptions.rowCount()):
                try:
                    gr_key = self.gridOptions.item(linha, 0).text()
                    if gr_key in include_list:
                        self.gridOptions.item(linha, 1).setText('1')
                    else:
                        if gr_key in ['clockin','backoffice','backupoff','gestm']:
                            self.gridOptions.item(linha,1).setText('')
                except KeyError:
                    pass
            self.validate_lic()
            
    def grid_change(self):
        try:
            sum = float(self.com_version_data['p1'])
        except (KeyError, TypeError):
            sum = 0.0
        for linha in range(0, self.gridOptions.rowCount()):
            try:
                sum += int(self.gridOptions.item(linha, 1).text()) * float(self.gridOptions.item(linha, 3).text())
            except ValueError:
                pass
        self.total_public.setText(str(sum))
        
    def set_prices_zero_click(self):
        for linha in range(0, self.gridOptions.rowCount()):
            self.gridOptions.item(linha, 3).setText('0.00')

    def calc_date_end(self, c_date):
        self.date_valid.setDate(liblogos.get_renew_data(c_date.toPyDate()))

    def renew_lic(self):
        """ carrega a ultima licença pedida v2 licença seja qual for maior que -1 é uma redundancia"""
        sql = '''SELECT sf_id FROM software where sf_status >-1 and sf_unit_id =%s ORDER BY sf_id DESC LIMIT 1'''
        self.lic_id = libpg.query_one(sql, (self.unit_id,))[0]
        self.last_lic_dict = data_sets.licence_to_dict(self.lic_id)
        self.software_id = self.last_lic_dict['sf_version']
        """carrega dicionario com os dados da licenca da base de dados"""
        lic_dict = json.loads(self.last_lic_dict[6])['0']
        try:
            lic_dict['comercial_version'] = lic_dict['commercial_version']
            del lic_dict['commercial_version']
        except KeyError:
            pass
        self.un_morada.setText(self.unit_dict['un_morada'])
        self.un_cp.setText(str(self.unit_dict['un_cp']))
        self.un_localidade.setText(self.unit_dict['un_localidade'])
        self.header.setText(lic_dict['dc'])
        self.phones.setText(lic_dict['telefone'])
        stdio.read_field(self.cl_id, 'cl_id',self.client_dict)
        stdio.read_field(self.cl_nif, 'cl_nif', self.client_dict)
        stdio.read_field(self.cl_nome,'cl_nome', self.client_dict)
        stdio.read_field(self.cl_morada,'cl_morada', self.client_dict)
        stdio.read_field(self.cl_morada,'cl_morada', self.client_dict)
        stdio.read_field(self.cl_localidade,'cl_localidade', self.client_dict)
        stdio.read_field(self.cl_cp,'cl_cp', self.client_dict)
        stdio.read_field(self.cl_conservatoria,'cl_conservatoria', self.client_dict)
        stdio.read_field(self.cl_cap_social,'cl_cap_social', self.client_dict)

        self.date_contract.setDate(datetime.datetime.strptime(lic_dict['date_contract'],"%Y-%m-%d"))
        self.software_type.setCurrentText(lic_dict['software_name'].title())
        new_lic_dict = {}
        if self.last_lic_dict['sf_json_version'] == 1:
            if lic_dict['tables'] == 'True':
                new_lic_dict['pro'] = '1'
            if lic_dict['dma'] == 'True':
                new_lic_dict['pro'] = ''
                new_lic_dict['premium'] = '1'
            if lic_dict['units'] == '1':
                pass
            else:
                new_lic_dict['terminals'] = str(int(lic_dict['units'])-1)
            if lic_dict['clockin'] == 'True':
                new_lic_dict['clockin'] = '1'
        else:
            new_lic_dict = lic_dict
            """ força clockin """
            new_lic_dict['clockin'] = '1'
            if 'comercial_version_key' not in new_lic_dict:
                self.comercialVersionEdt.setText(new_lic_dict['comercial_version'])
            else:
                self.comercialVersionEdt.setText(new_lic_dict['comercial_version'])
                self.com_version_data = data_sets.get_comercial_version(new_lic_dict['comercial_version_key'])
            new_lic_dict['sector'] = liblogos.get_unit_setting1(self.unit_id, 16)
            new_lic_dict['serie'] = liblogos.get_unit_setting1(self.unit_id, 20)
            new_lic_dict['rdp'] = liblogos.get_unit_setting1(self.unit_id, 7)
            new_lic_dict['printon'] = liblogos.get_unit_setting1(self.unit_id, 29)
        
        for linha in range(0, self.gridOptions.rowCount()):
            try:
                gr_key = self.gridOptions.item(linha, 0).text()
                if new_lic_dict[gr_key]:
                    if new_lic_dict[gr_key] == 'N/D':
                        self.gridOptions.item(linha, 1).setText('')
                    else:
                        self.gridOptions.item(linha, 1).setText(new_lic_dict[gr_key])
            except KeyError:
                pass


    def refresh_form(self):
        stdio.read_field(self.cl_id, 'cl_id',self.client_dict)
        stdio.read_field(self.cl_nif, 'cl_nif', self.client_dict)
        stdio.read_field(self.cl_nome,'cl_nome', self.client_dict)
        stdio.read_field(self.cl_morada,'cl_morada', self.client_dict)
        stdio.read_field(self.cl_morada,'cl_morada', self.client_dict)
        stdio.read_field(self.cl_localidade,'cl_localidade', self.client_dict)
        stdio.read_field(self.cl_cp,'cl_cp', self.client_dict)
        stdio.read_field(self.cl_conservatoria,'cl_conservatoria', self.client_dict)
        stdio.read_field(self.cl_cap_social,'cl_cap_social', self.client_dict)
        stdio.read_field(self.header,'un_nome', self.unit_dict)
        stdio.read_field(self.un_morada,'un_morada', self.unit_dict)
        stdio.read_field(self.un_localidade,'un_localidade', self.unit_dict)
        stdio.read_field(self.un_cp,'un_cp', self.unit_dict)
        self.date_contract.setDate(datetime.datetime.now())
        self.date_valid.setDate(datetime.datetime.now() + relativedelta(years=1))
        self.software_id = 10

    def save_lic(self):
        if self.validate_lic():
            """cria dicionario"""
            self.make_lic_dict()
            """grava na base de dados"""
            sql = '''INSERT INTO software (sf_unit_id, sf_lic_json, sf_version, sf_date_contract,
                    sf_date_valid, sf_lic_type,sf_json_version, sf_status, sf_who) values (%s, %s, %s, %s, %s, %s,0,0,%s)'''
            data = (self.unit_id, self.make_lic_dict_to_string(), self.software_id, self.date_contract.date().toPyDate(),
                     self.date_valid.date().toPyDate(), self.lic_values['lictype_txt'], gl.user_dict['user_name'])
            libpg.execute_query(sql, data)
            self.order_num = str(libpg.query_one('SELECT sf_id FROM software ORDER BY sf_id DESC LIMIT 1', (True, ))[0])
            """envia e mail a partir do dic"""
            self.send_lic_mail()
            b = "Licença: " + self.order_num + " enviada com sucesso."
            QMessageBox.information(self, "Informação",b)
            self.close()

    def validate_lic(self):
        if self.software_id > 0:
            self.lic_values['software_name'] = self.software_type.currentText().upper()
            """ tem a chave da versão comercial"""
            try:
                if self.com_version_data['insoft_opt_code'] is None:
                    QMessageBox.warning(None, "Erro", "Falta a versão comercial!")
            except TypeError:
                QMessageBox.warning(None, "Erro", "Falta a versão comercial!")
            else:
                """verifica se tem os settings para esta versão"""
                sett_list = self.com_version_data['insoft_opt_settings'].split(',')
                sett_error = [True,'']
                for n in sett_list:
                    has_sett = libpg.query_one('select us_id from unit_settings where us_unit_id = %s and us_act_id = %s', (gl.unit_dict['un_id'], n))
                    if has_sett is None:
                        a = data_sets.get_settings_data(n)
                        sett_error[0] = False
                        sett_error[1] = sett_error[1] + '\n' + a[1]
                if sett_error[0]:
                    return True
                else:
                    QMessageBox.warning(None, "Erro", "Faltam os seguintes dados:\n " + sett_error[1])
        else:
            QMessageBox.warning(None, "Erro", "Falta  o <b>software</b>!")

        return False

    def send_lic_mail(self):
        """cria email em html"""
        subject = '🌠 ' + self.lic_values['lictype_txt'].upper()[0] + 'LIC-' + self.order_num.zfill(5) + '-' + self.cl_nif.text() + '-' + self.header.text()
        body_text = liblogos.lic_to_html(self.lic_values, 'Pedido de Licença ' + self.lic_values['lictype_txt'])
        msg_dict = {'sub': subject,'body': body_text}
        mailing_list = ['restware@espiridiao.net']
        mail_responce = smtpmail.send_mail_lic_order(mailing_list, msg_dict)
        if not mail_responce[0]:
            errorMessage = QErrorMessage(self)
            errorMessage.showMessage(mail_responce[1])

    def make_lic_dict_to_string(self):
        members = {'0': self.lic_values}
        return json.dumps(members)

    def make_lic_dict(self):
        # gera um json e grava-o na base de dados.
        self.lic_values['total_public'] = float(self.total_public.text())
        self.lic_values['zipname'] = self.header.text().lower().replace(' ', '_') + '_' + self.cl_nif.text()
        self.lic_values['dc'] = self.header.text()
        self.lic_values['ds'] = self.cl_nome.text()
        self.lic_values['morada_sede'] = self.cl_morada.text()
        self.lic_values['localidade_sede'] = self.cl_localidade.text()
        self.lic_values['cp_sede'] = self.cl_cp.text()
        self.lic_values['morada'] = self.un_morada.text()
        self.lic_values['cp1'] = self.un_cp.text()
        self.lic_values['cp2'] = ''
        self.lic_values['localidade'] = self.un_localidade.text()
        self.lic_values['telefone'] = self.phones.text()
        self.lic_values['nif'] = str(self.cl_nif.text())
        self.lic_values['cs'] = str(self.cl_cap_social.text())
        self.lic_values['crc'] = self.cl_conservatoria.text()
        self.lic_values['software'] = self.software_type.currentText()
        self.lic_values['version'] = self.software_version.text()
        self.lic_values['date_contract'] = self.date_contract.date().toPyDate().strftime("%Y-%m-%d")
        self.lic_values['date_valid'] = self.date_valid.date().toPyDate().strftime("%Y-%m-%d")
        self.lic_values['who'] = gl.user_dict['user_name']
        self.lic_values['sector'] = liblogos.get_unit_setting1(self.unit_id, 16)
        # self.lic_values['serie'] = liblogos.get_unit_setting1(self.unit_id, 20)
        # self.lic_values['rdp'] = liblogos.get_unit_setting1(self.unit_id, 7)
        self.lic_values['printon'] = liblogos.get_unit_setting1(self.unit_id, 29)
        self.lic_values['comercial_version'] = self.com_version_data['insoft_opt_name']
        self.lic_values['comercial_version_key'] = self.com_version_data['insoft_opt_code'] # self.comercial_version_key
        a = libpg.query_many('select unit_set_id, unit_set_name from unit_set_types where unit_set_id in(' + self.com_version_data['insoft_opt_settings'] + ')', (True,))
        opt_list = []
        for n in a:
            v = libpg.query_one('select us_value1, us_value2 from unit_settings where us_unit_id=%s and  us_act_id=%s', (self.unit_id, n[0]))
            if v is None:
                opt_list.append((n[1], 'n/d'))
            else:
                opt_list.append((n[1], v[0]))
        self.lic_values['option'] = opt_list
        insoft_options_list = []
        for linha in range(0, self.gridOptions.rowCount()):
            try:
                gr_key = self.gridOptions.item(linha, 0).text()
                self.lic_values[gr_key] = self.gridOptions.item(linha, 1).text()
                """só adiciona para impressão os que tiverem valor"""
                if not self.gridOptions.item(linha, 1).text() == '':
                    insoft_options_list.append((self.gridOptions.item(linha, 1).text(),
                                                self.gridOptions.item(linha, 2).text(),
                                                self.gridOptions.item(linha, 3).text()))
                else:
                    pass
        
            except KeyError:
                pass
        self.lic_values['insoft_options'] = insoft_options_list
        self.lic_values['header'] = self.header.text()
        self.lic_values['comments'] = self.comments_Text.toPlainText()

    def calc_len(self,text):
        self.hcounter.setNum(42 - len(self.header.text()))
        self.pcounter.setNum(9 - len(self.phones.text()))

    def posto_change(self, value):
        self.calc_lic()

    def make_lic_click (self):
        self.save_lic()

    def exit_click (self):
        self.close()

    def call_new(self):
        self.new_lic.setChecked(True)
        self.renew.setChecked(False)
        self.calc_lic()

    def call_renew(self):
        # print 'renew'
        self.new_lic.setChecked(False)
        self.renew.setChecked(True)
        self.calc_lic()

    def cp_drill_down(self):
        form = cp.CpSearch()
        form.exec_()
        if form.ret[0]:
            self.un_cp.setText(form.ret[2])

    def get_db_data(self):
        self.unit_dict = libpg.get_record_dic('''SELECT un_nome, un_morada, un_localidade, un_cp, un_cliente_id
                    from unidades where un_id = %s ''', (self.unit_id,))
        self.client_dict = libpg.get_record_dic('''SELECT  cl_id, cl_nif, cl_nome, cl_morada, cl_localidade, cl_cp,
                    cl_telefone, cl_cap_social, cl_conservatoria
                    from clientes where cl_id = %s ''', (self.unit_dict['un_cliente_id'],))

    def perc(self, part, whole):
        p = '0.' + str(part)
        return whole - (whole * float(p))

    def all_off(self):
        self.tables.setEnabled(False)
        self.bo.setEnabled(False)
        self.agd.setEnabled(False)
        self.competition.setEnabled(False)
        self.second_unit.setEnabled(False)
        self.change_nif.setEnabled(False)
        self.units.setEnabled(False)
        self.monitors.setEnabled(False)
        self.clock_in.setEnabled(False)
        # self.branch.setEnabled(False)
        self.dma_qtd.setEnabled(False)

    def all_on(self):
        self.tables.setEnabled(True)
        self.bo.setEnabled(True)
        self.agd.setEnabled(True)
        self.competition.setEnabled(True)
        self.second_unit.setEnabled(True)
        self.change_nif.setEnabled(True)
        self.units.setEnabled(True)
        self.monitors.setEnabled(True)
        self.clock_in.setEnabled(True)
        self.dma_qtd.setEnabled(True)

    def get_software(self):
        toto = []
        dum = libpg.query_many('''SELECT sft_software from software_type
                where  sft_active = True and sft_unit_type=%s
                order by sft_sort ASC''', ('10000000',))
        for n in dum:
            toto.append(n[0])
        return toto
    

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


def get_software_last_version():
    dum = libpg.query_many('''SELECT sversion_name from software_version
            where  sversion_active = True and sversion_software_id=%s ''', (10,))
    return dum[0][0]


def logic_to_int(value):
    if value == True:
        return '1'
    else:
        return '0'


def print2file(name,content):
    f = open(name,'w')
    print(content, file=f)
    

if __name__ == '__main__':
    pass
