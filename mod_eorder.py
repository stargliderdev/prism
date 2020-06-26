#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

from PyQt5.QtWidgets import QDialog, QLabel, QCheckBox, QVBoxLayout, QLineEdit, QTabWidget, QPushButton, \
    QWidget, QToolButton, QDateEdit, QPlainTextEdit, QMessageBox, QErrorMessage, QDesktopWidget, QTableWidget, QComboBox
from PyQt5.QtCore import Qt

from dateutil.relativedelta import relativedelta

import json
import qlib
import libpg
import smtpmail
# import liblogos
import eorder_lib
import qlib as qc
import data_sets
# import unit_management
import cp
import ex_grid


class MakeEorder(QDialog):
    def __init__(self, unit, parent=None):
        super(MakeEorder, self).__init__(parent)
        """ global vars """
        self.un_id = unit
        self.resize(800, 600)
        masterLayout = QVBoxLayout(self)
        self.center()
        self.software_id = -1
        # # vars
        self.discount_table = {0: (0, 0), 1: (0,40), 2: (40, 0), 3: (40, 0), 4: (0, 40), 5: (25, 40)}
        self.values = {}
        """ make tabs """
        self.tabuladorTabWidget = QTabWidget()
        self.make_order_tab()
        self.tabuladorTabWidget.addTab(self.tab1, 'Licença')
        self.make_client_tab()
        # self.tabuladorTabWidget.addTab(self.tab2, 'Sede Social')
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
        
        masterLayout.addLayout(qc.addHLayout([make_Btn, exitBtn]))
        
        self.get_db_data(self.un_id)
        self.mail_to_insoft.setChecked(True)
        # vai buscar o ultimo pedido de eorder
        sql = '''select mo_id, mo_options_json
            from modules
            where mo_unit_id=%s
            order by mo_id desc limit 1'''
        last_eorder = libpg.query_one(sql, (self.un_id,))
        if last_eorder == None:
            self.refresh_form()
            self.fill_form_compat()
        else:
            self.refresh_form()
            self.fill_form(last_eorder)
            
    
    def make_order_tab(self):
        self.tab1 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab1)
        tabLayout = QVBoxLayout()
        self.header = QLineEdit()
        self.header.setMaxLength(42)
        self.header.setReadOnly(True)
        tabLayout.addLayout(qlib.addHLayout(['Nome', self.header,True], lw=120))
        self.cl_nome = QLineEdit()
        self.cl_nome.setMaxLength(50)
        self.cl_nome.setMaximumWidth(300)
        self.cl_nome.setReadOnly(True)
        tabLayout.addLayout(qlib.addHLayout(['D. Social', self.cl_nome, True], lw=120))

        self.un_morada = QLineEdit()
        self.un_morada.setReadOnly(True)
        self.un_morada.setMaxLength(255)
        self.un_morada.setMaximumWidth(300)
        tabLayout.addLayout(qlib.addHLayout(['Morada', self.un_morada, True], lw=120))

        self.un_localidade = QLineEdit()
        self.un_localidade.setReadOnly(True)
        self.un_localidade.setMaxLength(35)
        self.un_localidade.setMaximumWidth(300)
        tabLayout.addLayout(qlib.addHLayout(['Localidade', self.un_localidade, True], lw=120))

        self.un_cp = QLineEdit()
        self.un_cp.setReadOnly(True)
        self.un_cp.setMaximumWidth(300)

        tabLayout.addLayout(qlib.addHLayout(['Código Postal', self.un_cp, True], lw=120))
        self.date_valid = QDateEdit()
        self.date_valid.setMaximumWidth(140)
        self.date_valid.setMinimumWidth(140)
        self.date_valid.setDisplayFormat("yyyy-MM-dd")
        self.date_valid.setDate(datetime.datetime.now() + relativedelta(years=1))
        self.date_valid.setCalendarPopup(True)
        # self.date_valid.setDate(liblogos.get_renew_data(datetime.datetime.now()))
        tabLayout.addLayout(qlib.addHLayout(['Validade',self.date_valid,True]))
        # grelha com as opções
        self.optionsGrid = QTableWidget()
        self.optionsGrid.setEditTriggers(QTableWidget.AnyKeyPressed)
        self.optionsGrid.verticalHeader().setDefaultSectionSize(20)
        self.optionsGrid.setAlternatingRowColors(True)
        self.optionsGrid.setStyleSheet("alternate-background-color: #89CFF0;")
        self.optionsGrid.verticalHeader().setVisible(False)
        self.optionsGrid.resizeColumnsToContents()
        ex_grid.make_grid(self.optionsGrid, headers=['ID', 'Valor', 'Modulo', 'Preço', 'D'],
                          col_width=[(0, 0), (1, 110), (2, 350), (3, 100), (4, 0)])
        bc = libpg.query_many(
            'SELECT eo_code, null as qtd, eo_name, eo_price/100 '
            'FROM eorder_opt WHERE eo_order <99 ORDER BY eo_order',
            (True,))
        ex_grid.grid_std(self.optionsGrid, data=bc, f_col=['s', 's', 's', 'd2'])
        self.optionsGrid.cellChanged.connect(self.eorder_opt_grid_change)
        
        tabLayout.addWidget(self.optionsGrid)
        
        tabLayout.addWidget(qc.HLine())
        self.totalPublicEdt = QLineEdit()
        self.totalPublicEdt.setMaximumWidth(60)
        self.totalPublicEdt.setMinimumWidth(60)
        self.totalPublicEdt.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.totalPublicEdt.editingFinished.connect(self.pvp_change)
        
        self.totalAgentEdt = QLineEdit()
        self.totalAgentEdt.setMaximumWidth(60)
        self.totalAgentEdt.setMinimumWidth(60)
        self.totalAgentEdt.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        setPricesZeroBtn = QPushButton('0.00')
        setPricesZeroBtn.setFocusPolicy(Qt.NoFocus)
        setPricesZeroBtn.clicked.connect(self.set_prices_zero_click)
        
        tabLayout.addLayout(
            qc.addHLayout(['PVP', self.totalPublicEdt, 'Agente', self.totalAgentEdt, True, setPricesZeroBtn],
                          label_align=Qt.AlignVCenter | Qt.AlignRight))
        
        self.totallnfornashEdt = QLineEdit()
        self.totallnfornashEdt.setMaximumWidth(60)
        self.totallnfornashEdt.setMinimumWidth(60)
        self.totallnfornashEdt.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        
        tabLayout.addLayout(
            qc.addHLayout(['p/ Infornash', self.totallnfornashEdt, True], label_align=Qt.AlignVCenter | Qt.AlignRight))
        
        tabLayout.addWidget(qc.HLine())
        
        self.mail_to_insoft = QCheckBox('Mail para o Paulo')
        self.mail_to_insoft.setChecked(True)
        self.discountLevelCbox = QComboBox()
        self.discountLevelCbox.addItems(['Nova', 'Agente'])
        self.discountLevelCbox.currentIndexChanged.connect(self.eorder_opt_grid_change)
        tabLayout.addLayout(qc.addHLayout([self.mail_to_insoft, 'Desconto', self.discountLevelCbox]))
        
        mainTabLayout.addLayout(tabLayout)
    
    def eorder_opt_grid_change(self):
        sum = 0.0
        for linha in range(0, self.optionsGrid.rowCount()):
            try:
                sum += int(self.optionsGrid.item(linha, 1).text()) * float(
                    self.optionsGrid.item(linha, 3).text())
            except ValueError:
                pass
        a = self.discount_table[self.discountLevelCbox.currentIndex()]
        
        hl = self.perc(a[0], sum)
        bc = self.perc(a[1], hl)
        self.totalAgentEdt.setText(str(bc))
        self.totalPublicEdt.setText(str(hl))
        self.totallnfornashEdt.setText(str(bc))
    
    def pvp_change(self):
        try:
            sum = float(self.totalPublicEdt.text())
        except ValueError:
            sum = 0.0
        a = self.discount_table[self.discountLevelCbox.currentIndex()]
        hl = self.perc(a[0], sum)
        bc = self.perc(a[1], hl)
        self.totalAgentEdt.setText(str(bc))
        self.totalPublicEdt.setText(str(hl))
        self.totallnfornashEdt.setText(str(bc))
    
    def set_prices_zero_click(self):
        for linha in range(0, self.optionsGrid.rowCount()):
            self.optionsGrid.item(linha, 3).setText('0.00')
    
    def make_client_tab(self):
        self.tab2 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab2)
        tabLayout = QVBoxLayout()
        
        self.cl_id = QLineEdit()
        self.cl_id.setMaxLength(4)
        self.cl_id.setMaximumWidth(100)
        self.cl_id.setReadOnly(True)
        self.cl_id.setStyleSheet("background-color: #dbf3ff;")
        tabLayout.addLayout(qlib.addHLayout(['#', self.cl_id, True], lw=120))
        
        self.cl_nif = QLineEdit()
        self.cl_nif.setReadOnly(True)
        self.cl_nif.setMaxLength(9)
        self.cl_nif.setMaximumWidth(100)
        tabLayout.addLayout(qlib.addHLayout(['NIF', self.cl_nif, True], lw=120))
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
        # self.cl_cp.setMaxLength(8)
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
    
    def calc_a_zero(self, i):
        if i == 2:
            self.totalAgentEdt.setText('0.00')
            self.totalPublicEdt.setText('0.00')
            self.totallnfornashEdt.setText('0.00')
            self.partner.setText('0.00')
            self.header.setReadOnly(True)
            self.phones.setReadOnly(True)
            self.all_off()
        else:
            self.all_on()
            self.calc_lic()
            self.header.setReadOnly(False)
            self.phones.setReadOnly(False)
       
    def convert_old_data(self, old, gr_key):
        # convert dict antigo para o novo
        bc = ''
        if old == 'True':
            bc = '1'
        else:
            bc = None
        if gr_key == 'units':
            bc = str(int(old) - 1)
        return bc
    
    def refresh_form(self):
        self.cl_id.setText(str(self.client['cl_id']))
        self.cl_nif.setText(self.client['cl_nif'])
        self.cl_nome.setText(self.client['cl_nome'])
        self.cl_morada.setText(self.client['cl_morada'])
        self.cl_morada.setText(self.client['cl_morada'])
        self.cl_localidade.setText(self.client['cl_localidade'])
        self.cl_cp.setText(self.client['cl_cp'])
        self.cl_conservatoria.setText(self.client['cl_conservatoria'])
        self.cl_cap_social.setText(self.client['cl_cap_social'])
        self.header.setText(self.unit['un_name'])
        self.un_morada.setText(self.unit['un_morada'])
        self.un_localidade.setText(self.unit['un_localidade'])
        self.un_cp.setText(self.unit['un_cp'])
            
    def fill_form(self, order):
        lic_dict = json.loads(order[1])['0']
        for linha in range(0, self.optionsGrid.rowCount()):
            try:
                gr_key = self.optionsGrid.item(linha, 0).text()
                if lic_dict[gr_key]:
                    self.optionsGrid.item(linha, 1).setText(lic_dict[gr_key])
            except KeyError:
                pass
        self.date_valid.setDate(datetime.datetime.strptime(lic_dict['date_valid'], '%Y-%m-%d') + relativedelta(years=1))
        try:
            if lic_dict['password'] == '':
                self.set_iws_in_grid()
        except KeyError:
            #          não existe password: procura nos setings
            # chama o modo de compatibilidade
            self.set_iws_in_grid()
    
    def set_iws_in_grid(self):
        linha = self.optionsGrid.rowCount() - 1
        password = libpg.query_one('select us_value1 from unit_settings where us_unit_id= %s and us_act_id=22',(self.un_id,))
        if password is not None:
            self.optionsGrid.item(linha, 1).setText(password[0])

    def fill_form_compat(self):
        # para manter a compatibilidade com a versão pre eorder
        linha = self.optionsGrid.rowCount() - 1
        password = libpg.query_one('select cm_value from comitments_unit where cm_unit_id= %s and cm_act_id=21',(self.un_id,))
        if password is not None:
            self.optionsGrid.item(linha, 1).setText(password[0])
        
    def dict_to_string(self,dit):
        members = {'0': dit}
        return json.dumps(members)

        
    def save_lic(self):
        err = (True, '')
        if not err[0]:
            QMessageBox.warning(None, "Erro", err[1])
        else:
            self.lic_dict = self.make_eorder_dict()
            sql = '''INSERT INTO modules (mo_unit_id, mo_options_json,mo_date_valid) values (%s, %s, %s)'''
            # gera dicionario e grava na base de dados
            data = (self.un_id, self.make_lic_dict_to_string(), self.date_valid.date().toPyDate())
            libpg.execute_query(sql, data)
            self.order_num = str(libpg.query_one('SELECT mo_id FROM modules ORDER BY mo_id DESC LIMIT 1', (True,))[0]).zfill(4)
            # actualiza os compromissos
            libpg.execute_query('DELETE FROM comitments_unit WHERE cm_unit_id=%s AND cm_act_id IN (18,7,8,9,10,5,11,20,21)', (self.un_id,))
            libpg.execute_query('DELETE FROM unit_settings WHERE us_unit_id=%s AND us_act_id IN (20,16,22,23)', (self.un_id,))
            libpg.execute_query('UPDATE comitments_unit SET cm_archive=True WHERE cm_unit_id=%s AND cm_act_id IN (23,24)', (self.un_id,))
            libpg.execute_query('INSERT INTO comitments_unit (cm_unit_id,cm_act_id,cm_value) VALUES (%s,%s,%s)', (self.un_id,24, self.lic_dict['date_valid']))
            libpg.execute_query('INSERT INTO unit_settings (us_unit_id,us_act_id,us_value1) VALUES (%s,%s,%s)', (self.un_id,20, self.lic_dict['serie']))
            libpg.execute_query('INSERT INTO unit_settings (us_unit_id,us_act_id,us_value1) VALUES (%s,%s,%s)', (self.un_id,23, self.lic_dict['connections']))
            libpg.execute_query('INSERT INTO unit_settings (us_unit_id,us_act_id,us_value1) VALUES (%s,%s,%s)',(self.un_id,22,self.lic_dict['password']))
            
            if self.mail_to_insoft.isChecked():
                self.send_eorder_mail()
                b = "Pedido de eOrder: " + str(int(self.order_num)) + " enviado com sucesso."
            else:
                b = "Pedido de eOrder: " + str(int(self.order_num)) + " gerado com sucesso."
            QMessageBox.information(self, "Informação", b)
            self.close()
    
    def send_eorder_mail(self):
        # cria email em html
        subject = 'EORD-' + self.order_num + '-' + str(self.cl_nif.text()) + '-' + str(self.header.text())
        body_text = eorder_lib.to_html(self.lic_dict, 'Pedido de eOrder ')
        msg_dict = {'sub': subject, 'body': body_text}
        mail_responce = smtpmail.send_mail_lic_order('restware@espiridiao.net', msg_dict)
        if mail_responce[0] == False:
            errorMessage = QErrorMessage(self)
            errorMessage.showMessage(mail_responce[1])
    
    def make_lic_dict_to_string(self):
        members = {'0': self.lic_dict}
        return json.dumps(members)
    
    def make_eorder_dict(self):
        # gera um json e grava-o na base de dados.
        self.values['agentdiscount'] = '40'
        self.values['total_public'] = float(self.totalPublicEdt.text())
        self.values['total_agent'] = float(self.totalAgentEdt.text())
        self.values['total_infornash'] = float(self.totallnfornashEdt.text())
        hl = {
            'dc': self.header.text(),
            'ds': self.cl_nome.text().strip(),
            'morada': self.un_morada.text(),
            'cp1': self.un_cp.text(),
            'cp2': '',
            'localidade': self.un_localidade.text(),
            'nif': self.cl_nif.text(),
            'software': 'eOrder',
            'date_valid': self.date_valid.date().toPyDate().strftime("%Y-%m-%d"),
            'total_public': self.values['total_public'],
            'total_agent': self.values['total_agent'],
            'total_infornash': self.values['total_infornash'],
            'header': self.header.text(),
            'comments': self.comments_Text.toPlainText()}
        bc = {}
        for linha in range(0, self.optionsGrid.rowCount()):
            bc[self.optionsGrid.item(linha, 0).text()] = self.optionsGrid.item(linha, 1).text()
            hl.update(bc)
        if hl['connections'] == '':
            hl['connections'] = '0'
        else:
            hl['connections'] = hl['connections']
        return hl
    
    
    def posto_change(self, value):
        self.calc_lic()
    
    def make_lic_click(self):
        self.save_lic()
    
    def exit_click(self):
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
    
    def perc(self, part, whole):
        p = '0.' + str(part)
        return whole - (whole * float(p))
   
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def get_db_data(self,eorder_id):
        self.unit = libpg.get_record_dic('''SELECT un_name, un_morada, un_localidade, un_cp, un_cliente_id
                    from unidades where un_id = %s ''', (eorder_id,))
        self.client = libpg.get_record_dic('''SELECT  cl_id, cl_nif,  cl_nome, cl_morada, cl_localidade, cl_cp,
                    cl_telefone, cl_cap_social, cl_conservatoria
                    from clientes where cl_id = %s ''', (self.unit['un_cliente_id'],))


def logic_to_int(value):
    if value == True:
        return '1'
    else:
        return '0'



if __name__ == '__main__':
    pass
