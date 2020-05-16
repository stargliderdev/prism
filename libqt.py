#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import platform
import sys
import string
import time
import datetime

from PyQt4.QtCore import *
from PyQt4.QtGui import *

def w(obj, dic = {}):
        a = type(obj)
        if a == QLineEdit:
            return str(obj.text())
        elif a == QCheckBox:
            return obj.isChecked()
        elif a == QPlainTextEdit:
            return str(obj.toPlainText())
        elif a == QComboBox:
            return dic[obj.currentText()]

def r(obj,var,field):
        a = type(obj)
        if a == QCheckBox:
            obj.setChecked(var[field])
        elif a == QLineEdit:
            obj.setText(var[field])
        elif a == QPlainTextEdit:
            obj.appendPlainText(var[field])
        elif a == QComboBox:
            obj.setEditText(var[field])


if __name__ == '__main__':
    pass