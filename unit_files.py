#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QLabel, QCheckBox, QVBoxLayout, QLineEdit, QTabWidget,QPushButton,\
QWidget, QToolButton, QDateEdit, QTextEdit, QMessageBox, QErrorMessage, QDesktopWidget,QTableWidget,QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import sys
import datetime

import qlib as qc
import os
import uuid

import stdio
import libpg
import data_sets
import parameters as gl


class AddUnitFile(QDialog):
    def __init__(self, unit_id, cl_nif, parent=None):
        super(AddUnitFile, self).__init__(parent)
        # self.resize(1024, 768)
        self.full_file_list = []
        self.unit_id = unit_id
        self.cl_nif = cl_nif  # para verificar o saft e os backup
        # self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowTitleHint)
        self.setWindowTitle('Adicionar Ficheiro')
        masterLayout = QVBoxLayout(self)
        self.un_fref_type = QComboBox()
        self.un_fref_type.addItems(gl.un_ftypes)
        # self.connect(self.un_fref_type, SIGNAL("currentIndexChanged(int)"), self.type_change)
        self.un_fref_type.currentIndexChanged.connect(self.type_change)
        
        masterLayout.addLayout(qc.addHLayout(['Tipo:', self.un_fref_type]))
        self.un_fref_who = QComboBox()
        self.un_fref_who.addItems(gl.ds_tecnicos)
        self.un_fref_date = QDateEdit()
        self.un_fref_date.setCalendarPopup(True)
        self.un_fref_date.setDate(datetime.datetime.now())
        self.un_fref_date.setDisplayFormat("dd.MM.yyyy")
        masterLayout.addLayout(qc.addHLayout(['Data', self.un_fref_date, "Quem", self.un_fref_who]))
        self.un_fref_des = QPlainTextEdit()
        self.un_fref_des.setMaximumHeight(50)
        masterLayout.addLayout(qc.addHLayout(['Descrição', self.un_fref_des]))
        self.un_fref_fname = QLineEdit()
        self.un_fref_fname.setReadOnly(True)
        self.un_fref_fname.setStyleSheet("background-color: #dbf3ff;")
        pick_file = QToolButton()
        pick_file.setText('...')
        # self.connect(pick_file, SIGNAL("clicked()"), self.pick_file_click)
        pick_file.clicked.connect(self.pick_file_click)
        
        masterLayout.addLayout(qc.addHLayout(['Ficheiro', self.un_fref_fname, pick_file]))
        self.save_btn = QPushButton('Guarda')
        self.save_btn.setEnabled(False)
        # self.connect(self.save_btn, SIGNAL("clicked()"), self.save_click)
        self.save_btn.clicked.connect(self.save_click)
        
        cancel_btn = QPushButton('Sair')
        # self.connect(cancel_btn, SIGNAL("clicked()"), self.cancel_click)
        cancel_btn.clicked.connect(self.cancel_click)
        
        masterLayout.addLayout(qc.addHLayout([self.save_btn, cancel_btn]))
    
    def type_change(self):
        pass
    
    def pick_file_click(self):
        mask = get_mask(gl.un_ftypes_dic[str(self.un_fref_type.currentText()).lower()])
        self.un_fref_fname.clear()
        _files = QFileDialog.getOpenFileNames(None, self.tr("Escolher ficheiro(s) " +
                                                            str(self.un_fref_type.currentText())),
                                              self.tr(gl.unit_file_path),
                                              mask)
        if not _files == '':
            file_list = ''  # só os nomes dos ficheiros
            self.full_file_list = []
            for n in _files:
                self.full_file_list.append(str(n))
                path_name, file_name = os.path.split(str(n))
                file_list += ',' + str(file_name)
                b = self.process_file(str(n))
                if b[0] < 0:  # erro ficheiro
                    QMessageBox.warning(None, "Erro no ficheiro " + file_name, b[1],QMessageBox.StandardButtons(QMessageBox.Ok))
                else:
                    self.save_btn.setEnabled(True)
                    self.un_fref_fname.setText(file_list)
                    gl.unit_file_path = str(path_name + '\\')
    
    def save_click(self):
        if self.un_fref_who.currentIndex() == 0:
            QMessageBox.warning(None, "erro", 'Sem operador',QMessageBox.StandardButtons(QMessageBox.Ok))
        else:
            for full_name in self.full_file_list:
                a = self.write_bin(full_name)
                if a[0] == -1:  # ficheiro não existe no disco
                    QMessageBox.warning(None, self.tr("Erro o ficheiro não existe no disco" + full_name),
                                        a[1],QMessageBox.StandardButtons(QMessageBox.Ok))
                elif a[0] == -2:  # ficheiro existe na bd
                    # não faz anda porque já foi processado na rotina write_bin
                    pass
                else:
                    self.un_fref_fname.setText('Ficheiro Gravado: ' + "{0:4.2f}".format(a[1]) + ' Mb')
                    self.save_btn.setEnabled(False)
                    self.close()
    
    def cancel_click(self):
        self.close()
    
    def process_file(self, f):
        a = str(f)
        f_type = gl.un_ftypes_dic[str(self.un_fref_type.currentText()).lower()]
        path_name, file_name = os.path.split(a)
        if f_type == 1:
            bc = self.check_saft_date(file_name)
            if bc[0] > 0:
                self.un_fref_date.setDate(datetime.datetime.strptime(bc[1], '%Y-%m-%d'))
        elif f_type == 2:
            bc = self.check_backup_date(file_name)
            if bc[0] > 0:
                self.un_fref_date.setDate(datetime.datetime.strptime(bc[1], '%Y%m%d'))
        else:
            bc = 1, 'Ficheiro certo!'
        return bc
    
    def write_bin(self, full_file_name):
        _description = str(self.un_fref_des.toPlainText())
        _user = str(self.un_fref_who.currentText())
        _uuid = str(uuid.uuid4())
        _f_type = gl.un_ftypes_dic[str(self.un_fref_type.currentText()).lower()]
        dum, file_name = os.path.split(full_file_name)
        # file_name = os.path.basename(gl.unit_file_path)
        extension = os.path.splitext(full_file_name)[1][1:].lower()
        sql = 'SELECT un_fref_file_uuid FROM unit_files_ref WHERE un_fref_fname=%s AND un_fref_unit = %s '
        data = (file_name, self.unit_id)
        file_on_db = libpg.query_one(sql, data)
        if file_on_db is None:
            if stdio.file_ok(full_file_name):
                a = libpg.write_unit_bin(full_file_name, _uuid)
                sql = """insert into unit_files_ref (un_fref_uuid, un_fref_unit, un_fref_des, un_fref_fname, un_fref_data,
                     un_fref_who, un_fref_ext, un_fref_file_uuid, un_fref_ftype, un_fref_source) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                data = (
                    _uuid, self.unit_id, _description, file_name, self.un_fref_date.date().toPyDate(), _user, extension,
                    _uuid,
                    _f_type,
                    1)
                if a[0] > 0:
                    libpg.execute_query(sql, data)
                return a
            else:
                return -1, 'File does not exists'
        else:
            res = QMessageBox.question(
                None,
                self.tr("Ficheiro já existente na Base de dados"),
                self.tr("""Um ficheiro com este <b>nome</b> e nesta <b>unidade</b> já existe na Base de Dados.
                            Queres substiuir por este?"""),
                QMessageBox.StandardButtons(
                    QMessageBox.Cancel |
                    QMessageBox.Save),
                QMessageBox.Save)
            if res == QMessageBox.Save:
                libpg.execute_query('DELETE FROM unit_files_ref WHERE unit_files_ref.un_fref_file_uuid = %s',
                                    (file_on_db[0],))
                libpg.execute_query('DELETE FROM unit_files WHERE unit_files.un_files_uuid = %s',
                                    (file_on_db[0],))
                a = libpg.write_unit_bin(full_file_name, _uuid)
                ''' este codigo é igual ao de cima'''
                sql = """insert into unit_files_ref (un_fref_uuid, un_fref_unit, un_fref_des, un_fref_fname, un_fref_data,
                                     un_fref_who, un_fref_ext, un_fref_file_uuid, un_fref_ftype, un_fref_source) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                data = (
                    _uuid, self.unit_id, _description, file_name, datetime.datetime.now(), _user, extension, _uuid, 1,
                    1)
                if a[0] > 0:
                    libpg.execute_query(sql, data)
                return a
            else:
                return -2, 'duplicado'
    
    def check_backup_date(self, file_name):
        f_nif = -1
        f_date = datetime.datetime.now().strftime('%Y%m/%d')
        bc = file_name.replace('-', '_')
        bc = bc.split('_')
        for n in range(0, len(bc)):
            if f_nif == -1:
                if is_int(bc[n]):
                    f_nif = int(bc[n])
            else:
                if is_date(bc[n]):  # descobriu a data
                    f_date = bc[n]
                    break
        if f_nif != int(self.cl_nif):
            return -1, 'Não é o mesmo NIF da Unidade'
        return f_nif, f_date
    
    def check_saft_date(self, file_name):
        f_nif = -1
        f_date = ''
        bc = file_name.split('_')
        for n in bc:
            if is_int(n):
                f_nif = int(n)
                if f_nif != int(self.cl_nif):
                    return -1, 'Não é o mesmo NIF'
            if is_date(n):
                f_date = n
                return f_nif, f_date
                break
        return -1, 'erro ao validar data/NIF'


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def is_date(string):
    from dateutil.parser import parse
    try:
        parse(string)
        return True
    except ValueError:
        return False


def get_mask(a):
    if a in (1, 8, 9):
        return "Compressed files (*.zip *.7z *.rar)"
    elif a in (6, 3):
        return "Image Files (*.jpg *.gif *.png *.bpm)"
    elif a == 2:
        return '*.backup'
    elif a == 4:
        return '*.eml'
    elif a == 7:
        return '*.pdf'
    elif a == 5:
        return "Reports Files (*.pdf *.xls *.xlsx *.csv)"
    elif a == 10:
        return "Inventory Files (*.csv *.xls *.xlsx *.xml)"


def main():
    data_sets.get_unit_files_types()
    data_sets.get_ds_tecnicos()
    app = QApplication(sys.argv)
    form = AddUnitFile()
    form.show()
    app.exec_()


if __name__ == '__main__':
    pass

