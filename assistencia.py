#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QTabWidget,QPushButton,QPlainTextEdit,\
       QWidget, QToolButton, QDateTimeEdit, QMessageBox, QTextEdit, QDesktopWidget,QTableWidget,QComboBox, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon,QFont
import datetime
import parameters as pa
import libpg
import process_save
import smtpmail
import asterisk_interface

import data_sets
import wizard_status as w_status
import liblogos
import ex_grid
import qlib as qc


class Assistencia(QDialog):
    def __init__(self, last_proc, unit_id,  parent = None):
        super(Assistencia,  self).__init__(parent)
        # self.resize(1024, 768)
        self.setWindowTitle('Assistencia')
         
        masterLayout = QHBoxLayout(self)
        self.mainLayout = QVBoxLayout()
        # buttonsLayout = QVBoxLayout()
        self.last_proc = last_proc
        self.clipboard = QApplication.clipboard()
        # vars
        # self.tags = tags
        try:
            self.as_anterior = last_proc['proc_montante']
        except KeyError:
            self.as_anterior = 0
       
        self.unit_dict = data_sets.unit_to_dic(unit_id)

        self.as_taberna = QLineEdit()
        self.as_taberna.setText(self.unit_dict['un_name'])
        self.as_taberna.setStyleSheet("background-color: #dbf3ff;")
        self.as_taberna.setReadOnly(True)
        
        self.mainLayout.addLayout(qc.addHLayout(['Unidade',self.as_taberna,True], lw= 100))

        self.tabuladorTabWidget = QTabWidget()

        self.mainLayout.addWidget(self.tabuladorTabWidget)

        self.make_tab_start()
        self.tabuladorTabWidget.addTab(self.tab1, 'Inicio')

        self.make_tab_end()
        self.tabuladorTabWidget.addTab(self.tab2, 'Termina')

        self.make_hardware()
        self.tabuladorTabWidget.addTab(self.tab4, 'Hardware')

        # há anteriro?
        if self.as_anterior > 0:
            self.make_tab_ass_anterior()
            self.tabuladorTabWidget.addTab(self.tab3, 'Anterior')

        self.closeBtn = QPushButton('Fechar')
        self.closeBtn.setMaximumWidth(50)
        self.closeBtn.clicked.connect(self.close_click)
        
        masterLayout.addLayout(self.mainLayout)

        self.assistencia_resolvidaBtn = QPushButton('Resolvido')
        self.assistencia_resolvidaBtn.clicked.connect(self.proc_close_click)
        
        self.assistencia_pendenteBtn = QPushButton('Fica Pendente')
        self.assistencia_pendenteBtn.clicked.connect(self.proc_pending_click)
        
        self.mainLayout.addLayout(qc.addHLayout([self.assistencia_resolvidaBtn, self.assistencia_pendenteBtn,self.closeBtn]))
        self.status_label = QLabel()
        self.status_label.setText('A Lançar Assistencia')

        self.mainLayout.addWidget(self.status_label)

    def make_tab_start(self):
        if pa.dos:
            font = QFont('courier new',10)
            font.setWeight(80)
            font.setBold(False)
        else:
            font = QFont("Bitstream Vera Sans Mono",12)
            font.setWeight(80)
            font.setBold(False)
        self.tab1 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab1)
        self.as_quem = QLineEdit()
        self.as_contacto = QLineEdit()
        self.as_origem = QComboBox()
        self.as_origem.addItems(['Call Center', 'Escritório', 'mail', 'Pessoal'])
        self.as_nivel = QComboBox()
        self.as_nivel.addItems(['Normal', 'Urgente'])
        mainTabLayout.addLayout(qc.addHLayout(['Quem:', self.as_quem,'Contacto:',self.as_contacto, 'Nivel', self.as_nivel, 'Origem:', self.as_origem, True]))
        self.as_data = QDateTimeEdit()
        self.as_data.setCalendarPopup(True)
        self.as_data.setDisplayFormat("dd.MMM.yyyy hh:mm")
        self.as_data.setDateTime(datetime.datetime.now())
        self.as_data.dateTimeChanged.connect(self.start_date_change)
        
        self.as_duracao = QDateTimeEdit()
        self.as_duracao.setDisplayFormat("hh:mm")
        self.as_duracao.dateTimeChanged.connect(self.duration_change)
        
        self.as_data_fim = QDateTimeEdit()
        self.as_data_fim.setCalendarPopup(True)
        self.as_data_fim.setDisplayFormat("dd.MMM.yyyy hh:mm")
        self.as_data_fim.setDateTime(datetime.datetime.now())
        self.as_data.dateTimeChanged.connect(self.end_date_change)
        
        self.as_tecnico = QComboBox()
        self.as_tecnico.addItems(pa.ds_tecnicos)
        self.as_meio = QComboBox()
        self.as_meio.addItems(pa.dsMeios)
        self.as_meio.setCurrentIndex(-1)
        self.as_meio.currentIndexChanged.connect(self.as_meio_change)

        mainTabLayout.addLayout(qc.addHLayout(['Inicio:', self.as_data, 'Duração:', self.as_duracao,
                                               'Técnico:', self.as_tecnico, 'Meio', self.as_meio, True]))

        self.as_marcaemodelo = QLineEdit()
        self.as_marcaemodelo.setMinimumWidth(200)
        self.as_ns = QLineEdit()
        mainTabLayout.addLayout(qc.addHLayout(['Modelo:',self.as_marcaemodelo,'N/S:',self.as_ns]))
        self.as_avaria = QTextEdit()
        self.as_avaria.setFont(font)
        self.as_avaria.setMinimumHeight(60)
        
        mainTabLayout.addLayout(qc.addHLayout(['Avaria:',self.as_avaria]))
        self.as_relatorio_interno = QPlainTextEdit()
        self.as_relatorio_interno.setFont(font)
        self.as_relatorio_interno.setMinimumHeight(200)
        self.as_relatorio_interno.setPlainText(pa.ass_relatorio_interno)

        mainTabLayout.addLayout(qc.addVLayout(['Relatório Interno',self.as_relatorio_interno]))
        asterisk_log_btn = QToolButton()
        asterisk_log_btn.setToolTip('Relatório do Asterisk')
        asterisk_log_btn.setIcon(QIcon('.//img//drill_down.png'))
        # self.connect(asterisk_log_btn, SIGNAL("clicked()"), self.analisa_click)
        asterisk_log_btn.clicked.connect(self.analisa_click)
        
        paste_last_scall = QToolButton()
        paste_last_scall.setToolTip('Cola o relatório da ultima assistencia')
        paste_last_scall.setIcon(QIcon('.//img//paste.png'))
        paste_last_scall.clicked.connect(self.last_scall_paste)
        
        self.as_asterisk = QPlainTextEdit()
        self.as_asterisk.setMinimumHeight(80)
        self.as_asterisk.setMaximumHeight(80)
        font = QFont()
        font.setFamily("Monospace")
        font.setWeight(60)
        self.as_asterisk.setFont(font)
        mainTabLayout.addLayout(qc.addHLayout(['Relatorio do Asterisk', asterisk_log_btn, True, paste_last_scall], lw=150 ))
        mainTabLayout.addWidget(self.as_asterisk)
        # self.as_tags = QTextEdit()
        # self.as_tags.setMaximumHeight(40)
        # self.as_tags.setText(','.join(self.tags))
        # self.as_tags.setText(self.tags)
        # mainTabLayout.addLayout(qc.addVLayout(['Tags',self.as_tags]))
        mainTabLayout.addStretch()

    def make_tab_end(self):
        self.tab2 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab2)
        self.as_debito = QLineEdit()
        self.as_debito.setAlignment(Qt.AlignLeft)

        mainTabLayout.addLayout(qc.addHLayout(['Meio', self.as_debito]))
        # self.as_relatorio_interno = QPlainTextEdit()
        # # self.as_relatorio_interno.setMaximumHeight(100)
        # self.as_relatorio_interno.setPlainText(pa.ass_relatorio_interno)
        self.as_relatorio_factura = QTextEdit()
        self.as_relatorio_factura.setPlainText('')
        self.as_relatorio_factura.setMaximumHeight(100)
        mainTabLayout.addLayout(qc.addVLayout(['Relatório para Facturação',self.as_relatorio_factura,True]))
        self.as_meio_change(0)

    def make_tab_ass_anterior(self):
        self.tab3 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab3)
        self.as_montanteLabel = QTextEdit()
        self.as_montanteLabel.setMaximumHeight(150)
        self.as_montanteLabel.setReadOnly(True)

        self.as_relatorio_interno_montante = QPlainTextEdit()
        self.as_relatorio_interno_montante.setReadOnly(True)
        mainTabLayout.addLayout(qc.addVLayout(['Referente a:', self.as_montanteLabel, self.as_relatorio_interno_montante]))
        toto = '# ' + str(self.last_proc['proc_id']) + '<b> de </b> ' + self.last_proc['proc_date'].strftime('%d.%b.%Y %H:%M') + '<br>'
        toto += self.last_proc['proc_quem'] + ' ' + self.last_proc['proc_contacto'] + '<br>'
        toto += self.last_proc['proc_meio'] + '<br>'
        toto += self.last_proc['proc_reported'] + '<br><hr>'
        try:
            toto += self.last_proc['proc_model'] + '<br>'
        except TypeError:
            pass
        self.as_montanteLabel.setHtml(toto)
        self.as_relatorio_interno_montante.setPlainText(self.last_proc['proc_report_internal'])
        self.as_avaria.setText(self.last_proc['proc_reported'])

    def make_hardware(self):
        self.tab4 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab4)
        btn_layout = QHBoxLayout()
        refresh_Btn = QPushButton('Actualiza')
        refresh_Btn.clicked.connect(self.refresh_hw_click)
        
        btn_layout.addLayout(qc.addHLayout([refresh_Btn, True]))
        mainTabLayout.addLayout(btn_layout)
        self.gridHardware = QTableWidget(self)
        self.gridHardware.setSelectionBehavior(QTableWidget.SelectRows)
        self.gridHardware.setSelectionMode(QTableWidget.SingleSelection)

        self.gridHardware.setEditTriggers(QTableWidget.NoEditTriggers)
        self.gridHardware.verticalHeader().setDefaultSectionSize(20)
        self.gridHardware.setAlternatingRowColors (True)
        self.gridHardware.verticalHeader().setVisible(False)
        self.gridHardware.resizeColumnsToContents()
        self.gridHardware.itemDoubleClicked.connect(self.grid_click)
        mainTabLayout.addWidget(self.gridHardware)

    def refresh_hw_click(self):
        sql = '''select br_name , md_name as model,hw_type_name,
                 hw_sn, hwd_status_name
                 from hardware
                 inner join  models on hw_model_id = md_id
                 inner join  hw_status on hw_status.hwd_status_id = hardware.hw_status_id
                 inner join brands on md_brand_id = br_id
                 inner join hardware_types on hw_type_id = md_hardware_type
                 where hw_unit_id = %s
                 order by hw_type_order ;'''
        dataset = libpg.query_many(sql, (self.unit_dict['un_id'],))
        ex_grid.make_grid(self.gridHardware, ['Marca', 'Modelo', 'Tipo', 'Num. Série', 'Estado'],
                          [(0, 200), (1, 240), (2, 120), (3, 180), (4, 80)])
        ex_grid.grid_std(self.gridHardware, data=dataset, f_col=['s', 's', 's', 's', 's'])
        # ex_grid.ex_grid_update(self.gridHardware, {0:['Marca', 's'], 1:['Modelo', 's'], 2:['Tipo', 's'], 3:['S/N', 's'], 4:['Estado', 's']}, dataset)
        # self.grid.setColumnWidth(0, 50)
        # self.hardwareGrid.resizeColumnsToContents()

    def grid_click(self):
        md = self.gridHardware.item(self.gridHardware.currentRow(), 0).text() + ' ' + self.gridHardware.item(self.gridHardware.currentRow(), 1).text()
        self.as_marcaemodelo.setText(md)
        self.as_ns.setText(self.gridHardware.item(self.gridHardware.currentRow(), 3).text())
        self.tabuladorTabWidget.setCurrentIndex(0)

    def as_meio_change(self, id):
        if id == 0:
            self.as_debito.setText('FACTURAR DESLOCAÇÂO.')
        else:
            self.as_debito.setText('SEM CUSTOS.')

    def set_invoice_status(self):
        id = self.as_meio.currentIndex()
        if id == 0:
            self.facturar = True
        else:
            if self.as_relatorio_factura.toPlainText() == '':
                self.facturar = False
            else:
                self.facturar = True

    def close_click(self):
        self.close()

    def proc_close_click(self):
        error = self.valida()
        if error == []:
            self.as_status = 'Resolvido'
            self.pendente = False
            self.set_invoice_status()
            # grava
            self.ass_jusante = 0  # fechou
            self.grava_pedido()
            smtpmail.send_process_mail(self.process_id)
            liblogos.log_actions(pa.user_dict, 'proc close', 'pedido #' + str(self.process_id))
            self.close()
        else:
            self.show_error(error)

    def proc_pending_click(self):
        error = self.valida()
        if error == []:
            # 'grava'
            form = w_status.WizardStatus()
            form.exec_()
            if form.toto == -1:
                pass
            else:
                self.as_status = form.toto
                self.pendente = True
                self.ass_jusante = -1 # não fechou
                self.as_debito.setText('SEM CUSTOS.')
                self.facturar = False
                self.grava_pedido()
                # self.send_mail(self.as_taberna.text(),self.num_pedido)
                smtpmail.send_process_mail(self.process_id)
                liblogos.log_actions(pa.user_dict, 'ticket pending', 'pedido #' + str(self.process_id))
                # self.send_sms()
                self.close()
        else:
            self.show_error(error)
            
    def grava_pedido(self):
        self.status_label.setText('A gravar assistencia')
        self.status_label.repaint()
        data_dict = {'proc_date': self.as_data.dateTime().toPyDateTime(), 'proc_updated': datetime.datetime.now(),
                     'proc_unit_id': self.unit_dict['un_id'], 'proc_tecnico': self.as_tecnico.currentText(),
                     'proc_report_internal': self.as_relatorio_interno.toPlainText(), 'proc_serial_number': self.as_ns.text(),
                     'proc_report_invoice': self.as_debito.text() + ' ' + self.as_relatorio_factura.toPlainText(),
                     'proc_quem': self.as_quem.text(), 'proc_model': self.as_marcaemodelo.text(),
                     'proc_contacto': self.as_contacto.text(),
                     'proc_meio': self.as_meio.currentText(),
                     'proc_unit_name': self.unit_dict['un_name'],
                     'proc_reported': self.as_avaria.toPlainText(),
                     'proc_montante': self.as_anterior,
                     'proc_jusante': self.ass_jusante,
                     'proc_asterisk': self.as_asterisk.toPlainText(),
                     'proc_status': self.as_status, 'proc_nivel': self.as_nivel.currentText(),
                     'proc_facturar': self.facturar, 'proc_pendente': self.pendente, 'proc_facturado': False,
                     'proc_data_fim': self.as_data_fim.dateTime().toPyDateTime(),
                     'proc_duracao': str(self.as_duracao.dateTime().toPyDateTime().hour) + ':' + str(self.as_duracao.dateTime().toPyDateTime().minute)
                     }
        self.process_id = process_save.ticket(data_dict)
        self.status_label.setText('Terminada a gravação')
        self.status_label.repaint()

    def valida(self):
        error_list = []
        if not self.check_obj(self.as_quem):
            error_list.append('Falta responsavel!')
        if not self.check_obj(self.as_relatorio_interno):
            error_list.append('Falta relatorio interno!')

        if self.as_tecnico.currentIndex() == 0:
            error_list.append('Falta o Técnico')
        # if self.as_status.text() == 'n/d':
        #     pa.error_list.append('Falta o estado da assistencia')

        if self.as_duracao.time().minute()<1 and self.as_duracao.time().hour()==0:
            error_list.append('Ninguem faz nada em menos de um minuto')

        if self.as_meio.currentIndex() == -1:
            error_list.append('Falta o meio de resolução.')

        if error_list == []: # testa as datas
            ultima_assistencia = libpg.query_one('select max(assistencias.proc_date) from assistencias', (True,))[0]
             #print ultima_assistencia,'<=',self.as_data.dateTime().toPyDateTime()
            if ultima_assistencia <= self.as_data.dateTime().toPyDateTime():
                if datetime.datetime.now() < self.as_data.dateTime().toPyDateTime():
                     error_list.append('Assistencia no futuro!!!')
            else:
                 QMessageBox.critical(None,"Faltam os seguintes dados",'Data inferior á da ultima assistencia!\nMas lá passa!')
                 #pa.error_list.append('Data inferior á da ultima assistencia')

        return error_list

    def duration_change(self, ti):
        d = self.as_data.dateTime().toPyDateTime()

    def start_date_change(self,ti):
        d = self.as_data.dateTime().toPyDateTime()
    
    def end_date_change(self, ti):
        dum = self.as_data_fim.dateTime().toPyDateTime() - self.as_data.dateTime().toPyDateTime()
        
    def copy_to_master(self):
        self.as_relatorio_master.setPlainText(self.as_relatorio_interno.toPlainText())

    def copy_to_client(self):
        self.as_relatorio_cliente.setPlainText(self.as_relatorio_interno.toPlainText())
        
    def show_error(self, error_list):
            QMessageBox.critical(None,"Faltam os seguintes dados",'\n'.join(error_list))
            pa.error_list = [] 



    def last_scall_paste(self):
        self.as_relatorio_interno.setPlainText('\n—^—^—^—^—^—^—^—^— \n[' + str(self.last_proc['proc_id']) + '] de ' +
                self.last_proc['proc_date'].strftime('%d.%b.%Y %H:%M') + '\n' + self.as_relatorio_interno_montante.toPlainText())

    def analisa_click(self):
        form = asterisk_interface.AsteriskInterface()
        form.exec_()
        if form.toto['call_number'] == '':
            pass
        else:
            self.as_data.setDateTime(form.toto['call_date'])
            self.as_data_fim.setDateTime(form.toto['call_date'])
            self.as_contacto.setText(form.toto['call_number'])
            dum = str(form.toto['call_time'])
            self.as_quem.setText(form.toto['call_who'])
            # print 'dum',dum
            date_object = datetime.datetime.strptime(dum,"%H:%M:%S")
            self.as_duracao.setDateTime(date_object)
            self.as_asterisk.setPlainText(form.toto['call_cdr'])

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setSizes(self, object,value):
        object.setMaximumHeight (value)
        object.setMinimumHeight(value)
        object.setMaximumWidth(value+20)
        object.setMinimumWidth(value+20)

    def setSizeWidth(self, object, value):
        object.setMaximumWidth(value)
        object.setMinimumWidth(value)

    def setSizeHeight(self, object, value):
        object.setMaximumHeight(value)
        object.setMinimumHeight(value)

    def setBtnSizes(self, object,value=60):
        object.setMaximumHeight (value)
        object.setMinimumHeight(value)
        object.setMaximumWidth(value)
        object.setMinimumWidth(value)

    def check_obj(self, obj):
        if type(obj) == QLineEdit:
            if obj.text()=='':
                return False
            else:
                return True
        if type(obj) == QPlainTextEdit:
            if obj.toPlainText() == '':
                return False
            else:
                return True


if __name__ == '__main__':
    pass
