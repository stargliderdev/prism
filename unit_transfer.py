#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QLabel, QCheckBox, QVBoxLayout, QLineEdit, QPushButton,QDesktopWidget

import liblogos
import qlib as qc
import libpg
import parameters as gl


class UnitTransfer(QDialog):
    def __init__(self, parent=None):
        super(UnitTransfer, self).__init__(parent)
        self.resize(600, 400)
        self.center()
        self.setWindowTitle('Transfere dados entre Unidades')
        masterLayout = QVBoxLayout(self)
        self.unitSource = QLineEdit()
        self.unitSource.setMaximumWidth(50)
        self.unitSourceLabel = QLabel()
        self.unitSource.returnPressed.connect(self.source_change)
        
        self.unitTarget = QLineEdit()
        self.unitTarget.setMaximumWidth(50)
        self.unitTarget.returnPressed.connect(self.target_change)
        
        self.unitTargetLabel = QLabel()
        
        self.settingsCheck = QCheckBox('Configurações')
        self.settingsCheck.setChecked(True)
        self.hardwareCheck = QCheckBox('Hardware')
        self.hardwareCheck.setChecked(True)
        self.contactsCheck = QCheckBox('Contactos')
        self.contactsCheck.setChecked(True)
        self.memoCheck = QCheckBox('Memória descritiva')
        self.memoCheck.setChecked(True)
        
        masterLayout.addLayout(qc.addHLayout(['Origem:', self.unitSource, self.unitSourceLabel, True]))
        masterLayout.addLayout(qc.addHLayout(['Destino:', self.unitTarget, self.unitTargetLabel,True]))
        masterLayout.addLayout(qc.addVLayout([self.settingsCheck,self.contactsCheck,self.memoCheck,self.hardwareCheck]))
        masterLayout.addStretch()
        okBtn = QPushButton('Valida')
        okBtn.setAutoDefault(False)
        okBtn.clicked.connect(self.save_click)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.setAutoDefault(False)
        cancelBtn.clicked.connect(self.cancel_btn_click)
        masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
    
    def cancel_btn_click(self):
        self.close()
    
    def save_click(self):
        if self.unitSource.text() == '':
            pass
        elif self.unitTarget.text() == '':
            pass
        else:
            unit_source = int(self.unitSource.text())
            unit_target = int(self.unitTarget.text())
            if self.settingsCheck.checkState():
                sql = 'delete from unit_settings where us_unit_id=%s'
                libpg.execute_query(sql, (unit_target,))
                sql = 'insert into unit_settings (us_act_id,us_value1,us_value2, us_unit_id) select us_act_id,us_value1,us_value2, %s from unit_settings where us_unit_id=%s'
                libpg.execute_query(sql, (unit_target,unit_source))
            if self.contactsCheck.checkState():
                sql = 'delete from contacts where ct_unit=%s'
                libpg.execute_query(sql, (unit_target,))
                sql = 'insert into contacts (ct_ctt_id,ct_value1,ct_value2, ct_unit) select ct_ctt_id,ct_value1,ct_value2, %s from contacts where ct_unit=%s'
                libpg.execute_query(sql, (unit_target,unit_source))
            if self.hardwareCheck.checkState():
                sql = 'update hardware set hw_unit_id = %s where hw_unit_id=%s and hw_status_id=1'
                libpg.execute_query(sql, (unit_target, unit_source))
            if self.memoCheck.checkState():
                sql = ' update unidades set un_descricao=(select un_descricao from unidades where un_id=%s) where un_id=%s '
                libpg.execute_query(sql, (unit_source,unit_target))
            liblogos.log_actions(gl.user_dict,'transfere unit', 'transfer unit from ' + self.unitSource.text() + ' to ' + self.unitTarget.text())
            self.close()
            
    def source_change(self):
        xl = libpg.query_one('select un_nome from unidades where un_id=%s ', (self.unitSource.text(),))
        print(xl)
        self.unitSourceLabel.setText(xl[0])
    
    def target_change(self):
        print('return tar')
        xl = libpg.query_one('select un_nome from unidades where un_id=%s and  un_activa=True', (self.unitTarget.text(),))
        if xl is None:
            self.unitTargetLabel.setText('unidade desactivada')
        else:
            self.unitTargetLabel.setText(xl[0])
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class HardwareTransfer(QDialog):
    def __init__(self, hardware_dict,  parent=None):
        super(HardwareTransfer, self).__init__(parent)
        self.resize(400, 200)
        self.center()
        self.setWindowTitle('Transfere equipamento para outra unidade')
        self.hardware_dict = hardware_dict
        self.ret = False
        masterLayout = QVBoxLayout(self)
        self.unitTarget = QLineEdit()
        self.unitTarget.setMaximumWidth(50)
        self.unitTarget.returnPressed.connect(self.target_change)
        self.unitTargetLabel = QLabel()
        masterLayout.addLayout(qc.addHLayout(['Destino:', self.unitTarget, self.unitTargetLabel, True]))
        masterLayout.addStretch()
        okBtn = QPushButton('Valida')
        okBtn.setAutoDefault(False)
        okBtn.clicked.connect(self.save_click)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.setAutoDefault(False)
        cancelBtn.clicked.connect(self.cancel_btn_click)
        masterLayout.addLayout(qc.addHLayout([okBtn, cancelBtn]))
    
    def cancel_btn_click(self):
        self.close()
    
    def save_click(self):
        if self.unitTarget.text() == '':
            pass
        else:
            unit_target = int(self.unitTarget.text())
            sql = 'update hardware set hw_unit_id=%s where hw_id = %s'
            libpg.execute_query(sql, (unit_target, self.hardware_dict['hw_id']))
            liblogos.log_actions(gl.user_dict, 'transfer unit hardware', 'from ' + self.hardware_dict['hw_sn'] + ' to ' + str(unit_target))
            liblogos.hardware_update_settings(unit_target)
            self.ret = True
            self.close()
    
    def target_change(self):
        xl = libpg.query_one('select un_nome from unidades where un_id=%s and  un_activa=True',
                             (self.unitTarget.text(),))
        if xl is None:
            self.unitTargetLabel.setText('unidade desactivada')
        else:
            self.unitTargetLabel.setText(xl[0])
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':
    pass
 