#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog,  QCheckBox, QVBoxLayout, QLineEdit, QComboBox,QPushButton, QMessageBox, QToolButton, QTextEdit
from PyQt5.QtGui import QIcon
from qtconsole.qt import QtCore

import libpg
import model_tags
import qlib as qc
import data_sets
import liblogos
import parameters as gl
import brands


class ModelEdit(QDialog):
    def __init__(self, md_id, brand_id, brand_name, parent=None):
        super(ModelEdit, self).__init__(parent)
        self.resize(600, 400)
        # vars
        self.model_id = md_id
        self.brand_id = brand_id
        
        self.setWindowTitle('Ficha do Modelo')
        # self.tabuladorTabWidget = QTabWidget()
        masterLayout = QVBoxLayout(self)
        self.md_id = QLineEdit()
        self.md_id.setMaximumWidth(80)
        # self.md_id.setReadOnly(True)
        # self.md_id.setStyleSheet("background-color: #dbf3ff;")
        # masterLayout.addLayout(qc.addHLayout(['ID', self.md_id, True], lw=150))
        self.md_name = QLineEdit()
        self.md_name.setMaxLength(40)
        masterLayout.addLayout(qc.addHLayout(['Modelo:', self.md_name], lw=150))
        self.md_brand_id = QLineEdit()
        self.md_brand_id.setReadOnly(True)
        self.md_brand_id.setMinimumWidth(200)
        self.md_brand_id.setMaximumWidth(200)
        self.md_brand_id.setReadOnly(True)
        self.md_brand_id.setStyleSheet("background-color: #dbf3ff;")
        brandChangeTBtn = QToolButton()
        brandChangeTBtn.setText('☢️')
    
        brandChangeTBtn.clicked.connect(self.change_brand)
        
        masterLayout.addLayout(qc.addHLayout(['Marca:', self.md_brand_id, True, brandChangeTBtn], lw=150))
        self.hw_type_name = QComboBox()
        self.hw_type_name.setMaximumWidth(250)
        self.hw_type_name.addItems(gl.hardware_types)
        masterLayout.addLayout(qc.addHLayout(['Tipo:', self.hw_type_name, True], lw=150))
        self.md_ref_oem = QLineEdit()
        self.md_ref_oem.setMinimumWidth(150)
        self.md_ref_oem.setMaxLength(30)
        masterLayout.addLayout(qc.addHLayout(['Ref. Fabricante:', self.md_ref_oem], lw=150))
        self.md_ref_gc = QLineEdit()
        self.md_ref_gc.setMaxLength(30)
        masterLayout.addLayout(qc.addHLayout(['Ref. Gestao Comercial:', self.md_ref_gc], lw=150))
        self.lifeSpanCbox = QComboBox()
        self.lifeSpanCbox.addItems(['6 meses', '12 meses', '24 meses', '36 meses', '48 meses', '60 meses'])
        self.disabelChk = QCheckBox('Descontinuado')
        masterLayout.addLayout(qc.addHLayout(['Ciclo de Vida:', self.lifeSpanCbox, True, self.disabelChk], lw=150))
        self.add_tag = QToolButton()
        self.add_tag.setIcon(QIcon('.//img//add2.png'))
        self.add_tag.clicked.connect(self.add_tags_click)
        
        masterLayout.addLayout(qc.addHLayout([self.add_tag, True]))
        self.md_tags_txt = QTextEdit()
        masterLayout.addLayout(qc.addVLayout([self.md_tags_txt]))
        masterLayout.addStretch()
        save_Btn = QPushButton('Grava')
        save_Btn.clicked.connect(self.update_model)
        
        masterLayout.addWidget(save_Btn)
        if self.model_id > 0:
            self.model_dict = data_sets.model_to_dict(self.model_id)
            self.tags_stack = self.get_tags()
            # self.lifeSpanCbox.setEnabled(False)
            self.refresh_form()
        else:
            self.md_brand_id.setText(brand_name)
    
    def refresh_form(self):
        self.md_id.setText(str(self.model_dict['md_id']))
        self.md_ref_oem.setText(self.model_dict['md_ref_oem'])
        self.md_name.setText(self.model_dict['md_name'])
        self.md_ref_gc.setText(self.model_dict['md_ref_gc'])
        self.md_brand_id.setText(self.model_dict['br_name'])
        self.md_tags_txt.setText(self.model_dict['md_tags'])
        self.hw_type_name.setCurrentText(self.model_dict['hw_type_name'])
        self.lifeSpanCbox.setCurrentIndex(self.model_dict['md_lifespan'])

    def insert_model(self):
        sql = '''INSERT INTO models( md_name, md_ref_gc, md_brand_id, md_ref_oem, md_tags, md_hardware_type, md_lifespan)
               VALUES (%s,%s,%s,%s,%s, (SELECT hw_type_id from hardware_types where lower(hw_type_name)=%s), %s)'''
        data = (self.md_name.text().upper(),self.md_ref_gc.text().upper(), self.brand_id,self.md_ref_oem.text().upper(),
                self.md_tags_txt.toPlainText(), self.hw_type_name.currentText().lower(),self.lifeSpanCbox.currentIndex())
        libpg.execute_query(sql, data)
        a = libpg.sql_query('''Select max(md_id)+1 as t from models''')[0][0]
        if not self.md_tags_txt.toPlainText():
            pass
        else:
            liblogos.update_model_tags(a, self.md_tags_txt.toPlainText().lower())
        self.close()

    def update_model(self):
        if self.model_id > 0:
            sql = '''UPDATE models
                        SET md_name=%s, md_ref_gc=%s, md_ref_oem=%s, md_tags=%s, md_lifespan= %s,
                            md_hardware_type = (select hw_type_id from hardware_types where lower(hw_type_name) = %s)
                        WHERE md_id= %s'''
            data = (self.md_name.text(), self.md_ref_gc.text().upper(), self.md_ref_oem.text(), self.md_tags_txt.toPlainText().lower(),self.lifeSpanCbox.currentIndex(),
                    self.hw_type_name.currentText().lower(),  self.model_dict['md_id'])
            libpg.execute_query(sql, data)
            if self.tags_stack != self.md_tags_txt.toPlainText():
                liblogos.update_model_tags(self.model_dict['md_id'], self.md_tags_txt.toPlainText())
        else:
            self.insert_model()
        self.close()
    
    def get_tags(self):
        sql = '''SELECT tags_model.tam_name FROM tag_md_refs, tags_model WHERE
                tag_md_refs.tam_tag_id = tags_model.tam_id and tam_model_id=%s;'''
        a = libpg.query_many(sql, (self.model_dict['md_id'],))
        tags = ''
        for n in a:
            tags += n[0].lower() + ','
        return tags.rstrip(',')
    
    def add_tags_click(self):
        self.save_warning = True
        form = model_tags.ModelTagsBrowser()
        form.exec_()
        if form.tag_list[0] == 0:
            self.md_tags_txt.setPlainText(form.tag_list[1])
        elif form.tag_list[0] == 1:
            self.md_tags_txt.setPlainText(self.md_tags_txt.toPlainText() + ',' + form.tag_list[1])

    def change_brand(self):
        form = brands.BrandsBrowser()
        form.exec_()
        if form.ret['brand_id'] > 0:
            sql = 'update models set md_brand_id = %s where md_id = %s'
            libpg.execute_query(sql, (form.ret['brand_id'], self.model_dict['md_id']))
            self.model_dict = data_sets.model_to_dict(self.model_id)
            self.tags_stack = self.get_tags()
            self.refresh_form()


class AddBrand(QDialog):
    def __init__(self, parent=None):
        super(AddBrand, self).__init__(parent)
        self.setWindowTitle('Adiciona Marca')
        masterLayout = QVBoxLayout(self)
        self.text_1 = QLineEdit()
        masterLayout.addLayout(qc.addHLayout(['Marca', self.text_1, True], lw=100))
        ok_Btn = QPushButton('Adiciona')
        ok_Btn.clicked.connect(self.save_click)
        cancela_Btn = QPushButton('Cancela')
        cancela_Btn.clicked.connect(self.cancel_btn_click)
        masterLayout.addLayout(qc.addHLayout([ok_Btn, cancela_Btn]))
    
    def cancel_btn_click(self):
        self.close()
    
    def save_click(self):
        a = libpg.query_one('select br_name from brands where lower(br_name)= %s', (self.text_1.text().lower(),))
        if a is None:
            libpg.execute_query('insert into brands (br_name) VALUES (%s)', (str(self.text_1.text()),))
            self.close()
        else:
            QMessageBox.warning(None, "Marca Duplicada", "Esta marca já existe!")


if __name__ == '__main__':
    pass
