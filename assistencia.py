#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QTabWidget,QPushButton,QPlainTextEdit,\
       QWidget, QToolButton, QDateTimeEdit, QMessageBox, QTextEdit, QDesktopWidget,QTableWidget,QComboBox, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon,QFont
import datetime

import hardware
import parameters as pa
import libpg
import process_save
import smtpmail
import asterisk_interface

import data_sets
import close_process as w_status
import liblogos
import ex_grid
import qlib as qc
import sticky
import wizard_status


class Assistencia(QDialog):
    def __init__(self, last_proc_dict, unit_id, parent = None):
        super(Assistencia,  self).__init__(parent)
        # self.resize(1024, 768)
        self.setWindowTitle('Assistencia')
        
        masterLayout = QHBoxLayout(self)
        self.mainLayout = QVBoxLayout()
        # buttonsLayout = QVBoxLayout()
        self.last_proc_dict = last_proc_dict
        self.clipboard = QApplication.clipboard()
        self.proc_internal_report = ''
        # vars
        # self.tags = tags
        try:
            self.as_anterior = last_proc_dict['proc_montante']
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

        # self.make_hardware()
        # self.tabuladorTabWidget.addTab(self.tab4, 'Hardware')

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
        mainTabLayout.addLayout(qc.addHLayout(['Quem:', self.as_quem,'Contacto:',self.as_contacto, 'Nivel', self.as_nivel, 'Origem:',self.as_origem,  True]))
        self.as_data = QDateTimeEdit()
        self.as_data.setCalendarPopup(True)
        self.as_data.setDisplayFormat("dd-MM-yyyy hh:mm")
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
        self.as_marcaemodelo.setReadOnly(True)
        self.as_marcaemodelo.setStyleSheet("background-color: #dbf3ff;")
        self.as_ns = QLineEdit()
        self.as_ns.setReadOnly(True)
        self.as_ns.setStyleSheet("background-color: #dbf3ff;")
        hardwareBtn = QToolButton()
        hardwareBtn.setToolTip('Equipamentos na Unidade')
        hardwareBtn.clicked.connect(self.hardware_in_unit)
        
        mainTabLayout.addLayout(qc.addHLayout(['Modelo:',self.as_marcaemodelo,'N/S:',self.as_ns, hardwareBtn]))
        self.proc_reported = QTextEdit()
        self.proc_reported.setFont(font)
        self.proc_reported.setMinimumHeight(60)
        self.proc_reported.setMaximumHeight(140)
        # self.proc_reported.tab.connect(self.)
        # self.proc_reported.keyPressEvent.connect(self.tab_process)
        

        labelIssue = QLabel('Avaria/Sintoma/Problema')
        labelIssue.setStyleSheet("font-weight: bold; color: #FF0000;")
        paste_last_issue = QToolButton()
        paste_last_issue.setToolTip('Cola o relatório da ultima avaria/sintoma')
        paste_last_issue.setIcon(QIcon('.//img//paste.png'))
        paste_last_issue.clicked.connect(self.last_issue_paste)
        mainTabLayout.addLayout(qc.addHLayout([labelIssue, True, paste_last_issue]))
        mainTabLayout.addWidget(self.proc_reported)
        self.proc_cause_report = QPlainTextEdit()
        self.proc_cause_report.setFont(font)
        self.proc_cause_report.setMinimumHeight(100)
        self.proc_cause_report.setMaximumHeight(100)
        labelCause = QLabel('Causa/Origem do problema')
        labelCause.setStyleSheet("font-weight: bold;color: #0066ff;")
        paste_last_cause = QToolButton()
        paste_last_cause.setToolTip('Cola o relatório da ultima causa')
        paste_last_cause.setIcon(QIcon('.//img//paste.png'))
        paste_last_cause.clicked.connect(self.last_cause_paste)
        mainTabLayout.addLayout(qc.addHLayout([labelCause,True,paste_last_cause]))
        mainTabLayout.addWidget(self.proc_cause_report)
        self.proc_action_report = QTextEdit()
        self.proc_action_report.setFont(font)
        self.proc_action_report.setMinimumHeight(60)
        self.proc_action_report.setMaximumHeight(100)
        labelAction = QLabel('Acção')
        labelAction.setStyleSheet("font-weight: bold;color: #33cc33;")
        paste_last_action = QToolButton()
        paste_last_action.setToolTip('Cola o relatório da ultima acção')
        paste_last_action.setIcon(QIcon('.//img//paste.png'))
        paste_last_action.clicked.connect(self.last_action_paste)
        internalReportTBtn = QToolButton()
        internalReportTBtn.setToolTip('Comentário/Relatório Interno')
        internalReportTBtn.setIcon(QIcon('.//img//sticky.png'))
        internalReportTBtn.clicked.connect(self.add_sticky_note)
  
        mainTabLayout.addLayout(qc.addHLayout([labelAction, True,internalReportTBtn,paste_last_action]))
        mainTabLayout.addWidget(self.proc_action_report)
        asterisk_log_btn = QToolButton()
        asterisk_log_btn.setToolTip('Relatório do Asterisk')
        asterisk_log_btn.setIcon(QIcon('.//img//drill_down.png'))

        asterisk_log_btn.clicked.connect(self.analisa_click)
        
        self.as_asterisk = QPlainTextEdit()
        self.as_asterisk.setMinimumHeight(30)
        self.as_asterisk.setMaximumHeight(30)
        font = QFont()
        font.setFamily("Monospace")
        font.setWeight(60)
        self.as_asterisk.setFont(font)
        mainTabLayout.addLayout(qc.addHLayout(['Relatorio do Asterisk', asterisk_log_btn, True], lw=140 ))
        mainTabLayout.addWidget(self.as_asterisk)
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
        # self.as_montanteLabel.setMaximumHeight(150)
        self.as_montanteLabel.setReadOnly(True)

        # self.as_relatorio_interno_montante = QPlainTextEdit()
        # self.as_relatorio_interno_montante.setReadOnly(True)
        mainTabLayout.addWidget(self.as_montanteLabel)
        toto = '# ' + str(self.last_proc_dict['proc_id']) + '<br>' + self.last_proc_dict['proc_date'].strftime('%d-%m-%Y %H:%M') + '<br>'
        toto += self.last_proc_dict['proc_quem'] + ' ' + self.last_proc_dict['proc_contacto'] + '<br>'
        toto += self.last_proc_dict['proc_meio'] + '<br>'
        toto += self.last_proc_dict['proc_reported'] + '<br><hr>'
        try:
            toto += self.last_proc_dict['proc_model'] + '<br>'
        except TypeError:
            pass
        toto += self.last_proc_dict['proc_action_report']
        self.as_montanteLabel.setHtml(toto)
        # self.as_montanteLabel.setHtml()
        # self.as_avaria.setText(self.last_proc_dict['proc_reported'])

    # def make_hardware(self):
    #     self.tab4 = QWidget()
    #     mainTabLayout = QVBoxLayout(self.tab4)
    #     btn_layout = QHBoxLayout()
    #     refresh_Btn = QPushButton('Actualiza')
    #     refresh_Btn.clicked.connect(self.refresh_hw_click)
    #
    #     btn_layout.addLayout(qc.addHLayout([refresh_Btn, True]))
    #     mainTabLayout.addLayout(btn_layout)
    #     self.gridHardware = QTableWidget(self)
    #     self.gridHardware.setSelectionBehavior(QTableWidget.SelectRows)
    #     self.gridHardware.setSelectionMode(QTableWidget.SingleSelection)
    #
    #     self.gridHardware.setEditTriggers(QTableWidget.NoEditTriggers)
    #     self.gridHardware.verticalHeader().setDefaultSectionSize(20)
    #     self.gridHardware.setAlternatingRowColors (True)
    #     self.gridHardware.verticalHeader().setVisible(False)
    #     self.gridHardware.resizeColumnsToContents()
    #     self.gridHardware.itemDoubleClicked.connect(self.grid_click)
    #     mainTabLayout.addWidget(self.gridHardware)
    #
    def hardware_in_unit(self):
        form = hardware.HardwareBrw({'unit_id': self.unit_dict['un_id'], 'model_id': 0, 'un_name': self.unit_dict['un_name'], 'edit_mode': False})
        form.exec_()
        self.as_marcaemodelo.setText(form.ret['brand'] + '/' + form.ret['model'])
        self.as_ns.setText(form.ret['serial_number'])
    #
    # def refresh_hw_click(self):
    #     sql = '''select br_name , md_name as model,hw_type_name,
    #              hw_sn, hwd_status_name
    #              from hardware
    #              inner join  models on hw_model_id = md_id
    #              inner join  hw_status on hw_status.hwd_status_id = hardware.hw_status_id
    #              inner join brands on md_brand_id = br_id
    #              inner join hardware_types on hw_type_id = md_hardware_type
    #              where hw_unit_id = %s
    #              order by hw_type_order ;'''
    #     dataset = libpg.query_many(sql, (self.unit_dict['un_id'],))
    #     ex_grid.make_grid(self.gridHardware, ['Marca', 'Modelo', 'Tipo', 'Num. Série', 'Estado'],
    #                       [(0, 200), (1, 240), (2, 120), (3, 180), (4, 80)])
    #     ex_grid.grid_std(self.gridHardware, data=dataset, f_col=['s', 's', 's', 's', 's'])
    #     ex_grid.ex_grid_update(self.gridHardware, {0:['Marca', 's'], 1:['Modelo', 's'], 2:['Tipo', 's'], 3:['S/N', 's'], 4:['Estado', 's']}, dataset)
    #     self.grid.setColumnWidth(0, 50)
    #     self.hardwareGrid.resizeColumnsToContents()

    # def grid_click(self):
    #     md = self.gridHardware.item(self.gridHardware.currentRow(), 0).text() + ' ' + self.gridHardware.item(self.gridHardware.currentRow(), 1).text()
    #     self.as_marcaemodelo.setText(md)
    #     self.as_ns.setText(self.gridHardware.item(self.gridHardware.currentRow(), 3).text())
    #     self.tabuladorTabWidget.setCurrentIndex(0)

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
            form = wizard_status.WizardStatus()
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
        data_dict = {'proc_date': self.as_data.dateTime().toPyDateTime(), 'proc_updated': datetime.datetime.now(),
                     'proc_unit_id': self.unit_dict['un_id'], 'proc_tecnico': self.as_tecnico.currentText(),
                     'proc_reported': self.proc_reported.toPlainText(),
                     'proc_cause_report': self.proc_cause_report.toPlainText(),
                     'proc_action_report': self.proc_action_report.toPlainText(),
                     'proc_serial_number': self.as_ns.text(),
                     'proc_report_invoice': self.as_debito.text() + ' ' + self.as_relatorio_factura.toPlainText(),
                     'proc_quem': self.as_quem.text(),
                     'proc_model': self.as_marcaemodelo.text(),
                     'proc_contacto': self.as_contacto.text(),
                     'proc_meio': self.as_meio.currentText(),
                     'proc_unit_name': self.unit_dict['un_name'],
                     'proc_internal_report': self.proc_internal_report,

                     'proc_montante': self.as_anterior,
                     'proc_jusante': self.ass_jusante,
                     'proc_asterisk': self.as_asterisk.toPlainText(),
                     'proc_status': self.as_status,
                     'proc_nivel': self.as_nivel.currentText(),
                     'proc_facturar': self.facturar,
                     'proc_pendente': self.pendente,
                     'proc_facturado': False,
                     'proc_data_fim': self.as_data_fim.dateTime().toPyDateTime(),
                     'proc_duracao': str(self.as_duracao.dateTime().toPyDateTime().hour) + ':' + str(self.as_duracao.dateTime().toPyDateTime().minute)
                     }
        self.status_label.setText('A gravar assistencia')
        self.status_label.repaint()
        self.process_id = process_save.ticket(data_dict)
        self.status_label.setText('Terminada a gravação')
        self.status_label.repaint()

    def valida(self):
        error_list = []
        if not self.check_obj(self.as_quem):
            error_list.append('Falta responsavel!')
        if not self.check_obj(self.proc_cause_report):
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
        self.as_relatorio_master.setPlainText(self.proc_cause_report.toPlainText())

    def copy_to_client(self):
        self.as_relatorio_cliente.setPlainText(self.proc_cause_report.toPlainText())
        
    def show_error(self, error_list):
            QMessageBox.critical(None,"Faltam os seguintes dados",'\n'.join(error_list))
            pa.error_list = []

    def add_sticky_note(self):
        form = sticky.StickyNote(self.proc_internal_report)
        form.exec_()
        if form.ret[0]:
            self.proc_internal_report = form.ret[1]

    def tab_process(self, e):
        print("event", e)
        if e.key() == Qt.Key_Return:
            print(' return')
        elif e.key() == Qt.Key_Enter:
            print(' enter')

    def last_cause_paste(self):
        if not self.last_proc_dict == {}:
               self.proc_cause_report.setPlainText('\n────────────────────────────────────\n[' + str(self.last_proc_dict['proc_id']) + '] de ' +
                                                   self.last_proc_dict['proc_date'].strftime('%d.%b.%Y %H:%M') + '\n' + self.last_proc_dict['proc_action_report'])
            
            
    def last_issue_paste(self):
        if not self.last_proc_dict == {}:
               self.proc_cause_report.setPlainText('\n────────────────────────────────────\n[' + str(self.last_proc_dict['proc_id']) + '] de ' +
                                                   self.last_proc_dict['proc_date'].strftime('%d.%b.%Y %H:%M') + '\n' + self.last_proc_dict['proc_action_report'])


    def last_action_paste(self):
        if not self.last_proc_dict == {}:
               self.proc_cause_report.setPlainText('\n────────────────────────────────────\n[' + str(self.last_proc_dict['proc_id']) + '] de ' +
                                                   self.last_proc_dict['proc_date'].strftime('%d.%b.%Y %H:%M') + '\n' + self.last_proc_dict['proc_action_report'])


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
