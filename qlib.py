#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QCheckBox, QVBoxLayout, QWidget, QLineEdit, QTextEdit, QPlainTextEdit,\
    QSpinBox, QComboBox, QDateEdit, QFrame
from PyQt5.QtCore import *

def checkBoxGrid(label=''):
    w = QWidget()
    l = QHBoxLayout(w)
    l.setContentsMargins(0,0,0,0)
    l.addStretch()
    c = QCheckBox(label)
    l.addWidget(c)
    l.addStretch()
    return w


def addHLayout(listobj1,lw=80, label_align=Qt.AlignVCenter|Qt.AlignRight):
    dumLayout = QHBoxLayout()
    for n in listobj1:
        if (type(n)==str) or (type(n) == str):
            toto = QLabel(n)
            toto.setMinimumWidth(lw)
            toto.setMaximumWidth(lw)
            toto.setAlignment(label_align)
            dumLayout.addWidget(toto)
        elif type(n) == bool:
            dumLayout.addStretch()
        else:
            dumLayout.addWidget(n)
    return dumLayout


def read_field(obj,field,dic):
    # try:
        a = type(obj)
        toto = dic[field]
        if toto == None:
            pass
        elif a == QCheckBox:
            obj.setChecked(toto)
        elif a == QLineEdit:
            if type(toto) == int :
                obj.setText(str(toto))
            else:
                obj.setText(toto.strip())
        elif a == QTextEdit:
            obj.setPlainText(toto)
        elif a == QPlainTextEdit:
            obj.setPlainText(toto)
        elif a == QSpinBox:
            obj.setValue(toto)
        elif a == QComboBox:
            obj.setEditable(True)
            obj.setEditText(toto)
        elif a == QDateEdit:
            obj.setDate(toto)


def write_field(obj, dic={}):
        a = type(obj)
        if a == QLineEdit:
            if int(obj.text()) == False:
                toto = str(obj.text())
            else:
                toto = int(obj.text())
            return toto
        elif a == QDateEdit:
            return obj.date().toPyDate()
        elif a == QCheckBox:
            return obj.isChecked()
        elif a == QPlainTextEdit or a == QTextEdit:
            return str(obj.toPlainText())
        elif a == QSpinBox:
            return obj.value()
        elif a == QComboBox:
            if dic == {}:
                return obj.currentText()
            else:
                return dic[obj.currentText()]

def addVLayout(listobj1):
    dumLayout = QVBoxLayout()
    for n in listobj1:
        if (type(n)==str) or (type(n) == str):
            dumLayout.addWidget(QLabel(n))
        elif type(n) == bool:
            dumLayout.addStretch()
        else:
            dumLayout.addWidget(n)
    return dumLayout

def HLine():
    toto = QFrame()
    toto.setFrameShape(QFrame.HLine)
    toto.setFrameShadow(QFrame.Sunken)
    return toto