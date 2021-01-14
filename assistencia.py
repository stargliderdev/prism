#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QTabWidget, QPushButton, \
    QPlainTextEdit, QWidget, QToolButton, QDateTimeEdit, QMessageBox, QTextEdit, QDesktopWidget, QTableWidget, \
    QComboBox, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
import datetime

import hardware
import html_maker
import parameters as gl
import process_save
import report_display
import smtpmail
import asterisk_interface

import data_sets
import liblogos
import qlib as qc
import sticky
import wizard_status


class Assistencia(QDialog):
    def __init__(self, last_proc_dict, unit_id, parent=None):
        super(Assistencia, self).__init__(parent)
        self.setWindowTitle('Assistencia')
        
        masterLayout = QHBoxLayout(self)
        self.mainLayout = QVBoxLayout()
        self.last_proc_dict = last_proc_dict
        self.clipboard = QApplication.clipboard()
        self.proc_internal_report = ''
        self.proc_type = 'ASS'
        self.facturar = False
        self.process_id = 0
        self.current_proc_data = []
        try:
            self.as_anterior = last_proc_dict['proc_montante']
        except KeyError:
            self.as_anterior = 0
        self.unit_dict = data_sets.unit_to_dic(unit_id)
        
        self.as_taberna = QLineEdit()
        self.as_taberna.setText(self.unit_dict['un_name'])
        self.as_taberna.setStyleSheet("background-color: #dbf3ff;")
        self.as_taberna.setReadOnly(True)
        
        self.mainLayout.addLayout(qc.addHLayout(['Unidade', self.as_taberna, True], lw=100))
        
        self.tabuladorTabWidget = QTabWidget()
        
        self.mainLayout.addWidget(self.tabuladorTabWidget)
        
        self.make_tab_start()
        self.tabuladorTabWidget.addTab(self.tab1, 'Inicio')
        
        self.make_tab_end()
        self.tabuladorTabWidget.addTab(self.tab2, 'Termina')
        
        self.closeBtn = QPushButton('Sair')
        self.closeBtn.setMaximumWidth(50)
        self.closeBtn.clicked.connect(self.close_click)
        
        masterLayout.addLayout(self.mainLayout)
        
        self.assistencia_resolvidaBtn = QPushButton('Resolvido')
        self.assistencia_resolvidaBtn.clicked.connect(self.proc_close_click)
        
        self.assistencia_pendenteBtn = QPushButton('Fica Pendente')
        self.assistencia_pendenteBtn.clicked.connect(self.proc_pending_click)
        
        self.mainLayout.addLayout(
            qc.addHLayout([self.assistencia_resolvidaBtn, self.assistencia_pendenteBtn, self.closeBtn]))
        if gl.asterisk_stack_call == {}:
            pass
        else:
            self.as_data.setDateTime(gl.asterisk_stack_call['call_date'])
            self.as_contacto.setText(gl.asterisk_stack_call['call_number'])
            self.as_quem.setText(gl.asterisk_stack_call['call_who'])
            self.as_duracao.setDateTime(gl.asterisk_stack_call['call_time'])
            self.as_asterisk.setPlainText(gl.asterisk_stack_call['call_cdr'])
            gl.asterisk_stack_call = {}
    
    def make_tab_start(self):
        if gl.dos:
            font = QFont('courier new', 10)
            font.setWeight(80)
            font.setBold(False)
        else:
            font = QFont("Bitstream Vera Sans Mono", 12)
            font.setWeight(80)
            font.setBold(False)
        self.tab1 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab1)
        asterisk_log_btn = QToolButton()
        asterisk_log_btn.setToolTip('Relatório do Asterisk')
        asterisk_log_btn.setIcon(QIcon('.//img//asterisk.png'))
        asterisk_log_btn.clicked.connect(self.get_asterisk_data_click)
        self.as_quem = QLineEdit()
        self.as_contacto = QLineEdit()
        self.proc_origemBox = QComboBox()
        self.proc_origemBox.addItems(gl.proc_sources)
        
        self.lastProcBtn = QToolButton()
        self.lastProcBtn.setToolTip('Assistencia a Montante')
        self.lastProcBtn.setIcon(QIcon('.//img//last_proc.png'))
        self.lastProcBtn.setEnabled(False)
        self.lastProcBtn.clicked.connect(self.last_proc_show_click)
        
        self.procTypeCombo = QComboBox()
        self.procTypeCombo.addItems(gl.proc_type_show)
        self.procTypeCombo.currentTextChanged.connect(self.proc_type_change)
        
        self.as_nivel = QComboBox()
        self.as_nivel.addItems(['Normal', 'Urgente'])
        mainTabLayout.addLayout(qc.addHLayout(
            ['Nivel', self.as_nivel, 'Origem:', self.proc_origemBox, True, self.lastProcBtn, 'Tipo',
             self.procTypeCombo]))
        mainTabLayout.addLayout(
            qc.addHLayout(['Quem:', self.as_quem, 'Contacto:', self.as_contacto, asterisk_log_btn, True]))
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
        self.as_tecnico.addItems(gl.ds_tecnicos)
        self.as_meio = QComboBox()
        self.as_meio.addItems(gl.ds_proc_meios)
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
        self.hardwareBtn = QToolButton()
        self.hardwareBtn.setToolTip('Equipamentos na Unidade')
        self.hardwareBtn.clicked.connect(self.hardware_in_unit)
        
        mainTabLayout.addLayout(qc.addHLayout(['Modelo:', self.as_marcaemodelo, 'N/S:', self.as_ns, self.hardwareBtn]))
        labelIssue = QLabel('Avaria/Sintoma/Problema')
        labelIssue.setStyleSheet("font-weight: bold; color: #FF0000;")
        self.proc_reported = QTextEdit()
        self.proc_reported.setFont(font)
        self.proc_reported.setMinimumHeight(100)
        self.proc_reported.setMaximumHeight(100)
        
        paste_last_issue = QToolButton()
        paste_last_issue.setToolTip('Cola o relatório da ultima avaria/sintoma')
        paste_last_issue.setIcon(QIcon('.//img//paste.png'))
        paste_last_issue.clicked.connect(self.last_issue_paste)
        mainTabLayout.addLayout(qc.addHLayout([labelIssue, True, paste_last_issue]))
        mainTabLayout.addWidget(self.proc_reported)
        self.proc_cause_report = QTextEdit()
        self.proc_cause_report.setFont(font)
        self.proc_cause_report.setMinimumHeight(100)
        self.proc_cause_report.setMaximumHeight(100)
        labelCause = QLabel('Causa/Origem do problema')
        labelCause.setStyleSheet("font-weight: bold;color: #0066ff;")
        paste_last_cause = QToolButton()
        paste_last_cause.setToolTip('Cola o relatório da ultima causa')
        paste_last_cause.setIcon(QIcon('.//img//paste.png'))
        paste_last_cause.clicked.connect(self.last_cause_paste)
        mainTabLayout.addLayout(qc.addHLayout([labelCause, True, paste_last_cause]))
        mainTabLayout.addWidget(self.proc_cause_report)
        self.proc_action_report = QTextEdit()
        self.proc_action_report.setFont(font)
        self.proc_action_report.setMinimumHeight(100)
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
        
        mainTabLayout.addLayout(qc.addHLayout([labelAction, True, internalReportTBtn, paste_last_action]))
        mainTabLayout.addWidget(self.proc_action_report)
        
        self.as_asterisk = QPlainTextEdit()
        self.as_asterisk.setMinimumHeight(30)
        self.as_asterisk.setMaximumHeight(30)
        font = QFont()
        font.setFamily("Monospace")
        font.setWeight(60)
        self.as_asterisk.setFont(font)
        mainTabLayout.addWidget(self.as_asterisk)
        mainTabLayout.addStretch()
        try:
            if self.last_proc_dict['proc_id'] > 0:
                self.lastProcBtn.setEnabled(True)
        except KeyError:
            pass
    
    def make_tab_end(self):
        self.tab2 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab2)
        self.as_debito = QLineEdit()
        self.as_debito.setAlignment(Qt.AlignLeft)
        
        mainTabLayout.addLayout(qc.addHLayout(['Meio', self.as_debito]))
        self.as_relatorio_factura = QTextEdit()
        self.as_relatorio_factura.setPlainText('')
        self.as_relatorio_factura.setMaximumHeight(100)
        mainTabLayout.addLayout(qc.addVLayout(['Relatório para Facturação', self.as_relatorio_factura, True]))
        self.as_meio_change(0)
    
    def hardware_in_unit(self):
        form = hardware.HardwareBrw(
            {'unit_id': self.unit_dict['un_id'], 'model_id': 0, 'un_name': self.unit_dict['un_name'],
             'edit_mode': False})
        form.exec_()
        if form.ret == {}:
            pass
        else:
            self.as_marcaemodelo.setText(form.ret['brand'] + '/' + form.ret['model'])
            self.as_ns.setText(form.ret['serial_number'])
    
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
        """fecha"""
        error = self.valida_campos()
        if error == []:
            self.as_status = 'Resolvido'
            self.pendente = False
            self.set_invoice_status()
            # grava
            self.ass_jusante = 0  # fechou
            self.grava_pedido()
            smtpmail.send_process_mail(self.process_id)
            liblogos.log_actions(gl.user_dict, 'proc close', 'pedido #' + str(self.process_id))
            self.close()
        else:
            self.show_error(error)
    
    def proc_pending_click(self):
        """ pendente"""
        error = self.valida_campos(close_proc=False)
        if not error:
            # 'grava'
            form = wizard_status.SetPendingStatus()
            form.exec_()
            if form.toto == -1:
                pass
            else:
                self.as_status = form.toto
                self.pendente = True
                self.ass_jusante = -1  # não fechou
                self.as_debito.setText('SEM CUSTOS.')
                if self.proc_type == 'INFO':
                    self.facturar = False
                self.grava_pedido()
                smtpmail.send_process_mail(self.process_id)
                liblogos.log_actions(gl.user_dict, 'ticket pending', 'pedido #' + str(self.process_id))
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
                     'proc_duracao': str(self.as_duracao.dateTime().toPyDateTime().hour) + ':' + str(
                         self.as_duracao.dateTime().toPyDateTime().minute),
                     'proc_type': self.proc_type,
                     'proc_source': self.proc_origemBox.currentText()
                     }
        process_save.ticket(data_dict)
        self.process_id = gl.current_proc_data[0]
    
    def valida_campos(self, close_proc=True):
        error_list = []
        
        """ limpa as linhas vazias"""
        self.proc_reported.setText(
            "\n".join([ll.rstrip() for ll in self.proc_reported.toPlainText().splitlines() if ll.strip()]))
        self.proc_cause_report.setText(
            "\n".join([ll.rstrip() for ll in self.proc_cause_report.toPlainText().splitlines() if ll.strip()]))
        self.proc_action_report.setText(
            "\n".join([ll.rstrip() for ll in self.proc_action_report.toPlainText().splitlines() if ll.strip()]))
        
        if close_proc and self.proc_type in 'ASS':
            if self.proc_reported.toPlainText() == '':
                error_list.append('Falta Problema/Sintoma!')
            if self.proc_action_report.toPlainText() == '':
                error_list.append('Falta a Acção!')
        elif not close_proc and self.proc_type in 'ASS':
            if self.proc_reported.toPlainText() == '':
                error_list.append('Falta o Problema reportado!')
        if self.proc_type == 'INFO':
            if self.proc_internal_report == '':
                error_list.append('Como é uma INFORmação\n tem de ter comentário interno.')
        if self.proc_type == 'INT':
            if self.proc_action_report.toPlainText() == '':
                error_list.append('A Falta a Acção!')
        
        """ mandatórios """
        if not self.check_obj(self.as_quem):
            error_list.append('Falta responsavel!')
        if self.proc_origemBox.currentIndex() == 0:
            error_list.append('Falta a origem')
        if self.as_tecnico.currentIndex() == 0:
            error_list.append('Falta o Técnico')
        if self.as_duracao.time().minute() < 1 and self.as_duracao.time().hour() == 0:
            error_list.append('Ninguem faz nada em menos de um minuto')
        
        if self.as_meio.currentIndex() == -1:
            error_list.append('Falta o meio de actuação.')
        
        return error_list
    
    def duration_change(self, ti):
        d = self.as_data.dateTime().toPyDateTime()
    
    def start_date_change(self, ti):
        d = self.as_data.dateTime().toPyDateTime()
    
    def end_date_change(self, ti):
        dum = self.as_data_fim.dateTime().toPyDateTime() - self.as_data.dateTime().toPyDateTime()
    
    def copy_to_master(self):
        self.as_relatorio_master.setPlainText(self.proc_cause_report.toPlainText())
    
    def copy_to_client(self):
        self.as_relatorio_cliente.setPlainText(self.proc_cause_report.toPlainText())
    
    def show_error(self, error_list):
        QMessageBox.critical(None, "Faltam os seguintes dados", '\n'.join(error_list))
        gl.error_list = []
    
    def add_sticky_note(self):
        form = sticky.StickyNote(self.proc_internal_report)
        form.exec_()
        if form.ret[0]:
            self.proc_internal_report = form.ret[1]
    
    def tab_process(self, e):
        if e.key() == Qt.Key_Return:
            print(' return')
        elif e.key() == Qt.Key_Enter:
            print(' enter')
    
    def last_issue_paste(self):
        try:
            if self.last_proc_dict['proc_reported'] != '':
                self.proc_reported.setPlainText(comment_string(self.last_proc_dict['proc_reported']))
        except KeyError:
            pass
    
    def last_cause_paste(self):
        try:
            if self.last_proc_dict['proc_cause_report'] != '':
                self.proc_cause_report.setPlainText(comment_string(self.last_proc_dict['proc_cause_report']))
        except KeyError:
            pass
    
    def last_action_paste(self):
        try:
            if self.last_proc_dict['proc_action_report'] != '':
                self.proc_action_report.setPlainText(comment_string(self.last_proc_dict['proc_action_report']))
        except KeyError:
            pass
    
    def get_asterisk_data_click(self):
        form = asterisk_interface.AsteriskInterface()
        form.exec_()
        try:
            if form.toto['call_number'] == '':
                pass
            else:
                self.as_data.setDateTime(form.toto['call_date'])
                self.as_data_fim.setDateTime(form.toto['call_date'])
                self.as_contacto.setText(form.toto['call_number'])
                try:
                    self.as_quem.setText(form.toto['call_who'])
                except KeyError:
                    self.as_quem.setText('')
            
            self.as_duracao.setDateTime(form.toto['call_time'])
            self.as_asterisk.setPlainText(form.toto['call_cdr'])
        except KeyError:
            pass
    
    def last_proc_show_click(self):
        proc_dict = data_sets.process_to_dict(self.last_proc_dict['proc_id'])
        proc_html = html_maker.process_to_html(proc_dict)
        form = report_display.DisplayReport(proc_html)
        form.exec_()
    
    def proc_type_change(self, t):
        if t == 'INFO':
            self.proc_type = 'INFO'
            self.as_nivel.setEnabled(False)
            self.proc_reported.setEnabled(False)
            self.proc_cause_report.setEnabled(False)
            self.proc_action_report.setEnabled(False)
            self.assistencia_pendenteBtn.setEnabled(False)
            self.hardwareBtn.setEnabled(False)
            self.lastProcBtn.setEnabled(False)
            self.add_sticky_note()
        elif t == 'INT':
            self.proc_type = 'INT'
            self.proc_origemBox.setCurrentText('Interna')
            self.as_quem.setText(gl.user_dict['user_name'])
            self.as_contacto.setText('pessoal')
            self.as_meio.setCurrentText('Telemanutenção')
            self.as_tecnico.setCurrentText(gl.user_dict['user_name'].title())
        else:
            self.proc_type = 'ASS'
            self.as_nivel.setEnabled(True)
            self.proc_reported.setEnabled(True)
            self.proc_cause_report.setEnabled(True)
            self.proc_action_report.setEnabled(True)
            self.assistencia_pendenteBtn.setEnabled(True)
            self.hardwareBtn.setEnabled(True)
            self.lastProcBtn.setEnabled(True)
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def check_obj(self, obj):
        if type(obj) == QLineEdit:
            if obj.text() == '':
                return False
            else:
                return True
        if type(obj) == QPlainTextEdit:
            if obj.toPlainText() == '':
                return False
            else:
                return True


def comment_string(input_string):
    input_list = input_string.split('\n')
    out_string = ''
    for n in input_list:
        if len(n) > 0:
            out_string += '\u27A4' + n + '\n'
    return out_string


if __name__ == '__main__':
    pass
