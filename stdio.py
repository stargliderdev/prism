#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import datetime
from random import randrange
from decimal import Decimal
from PyQt5.QtWidgets import QLineEdit, QCheckBox, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox, QDateEdit


def write_field(obj, dic={}):
    a = type(obj)
    if a == QLineEdit:
        try:
            toto = int(obj.text())
        except ValueError:
            toto = str(obj.text())
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


def read_field(obj, field, dic):
    # try:
    a = type(obj)
    toto = dic[field]
    if toto == None:
        pass
    elif a == QCheckBox:
        obj.setChecked(toto)
    elif a == QLineEdit:
        if type(toto) == int:
            obj.setText(str(toto))
        elif type(toto) == Decimal:
            obj.setText('{0:.2f}'.format(toto))
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


# except Exception,e:
#
#     print 'erro em def read_field()'
#     print str(e)
#     print 'in field:', field
#     print 'in dic:',dic

def date_process(data, on_null='Vitalicio'):
    if data == None:
        return on_null
    else:
        return 0


def read_config_file(file_name):
    lines = []
    try:
        f = open(file_name, "r")
        try:
            lines = f.readlines()
        finally:
            f.close()
    except IOError:
        print('erro ao ler ini')
    return lines


def ini_file_to_dic(lines):
    dic = {}
    if not lines == []:
        for n in lines:
            dum = n.split('=')
            if len(dum) > 1:
                dic[dum[0]] = dum[1].strip('\n')
            else:
                dic[dum[0].strip('\n')] = None
        dic['error'] = False
    else:
        dic['error'] = True
    
    return dic


def print2file(name, content):
    f = open(name, 'w')
    print(content, file=f)


def read_file(file_name, mode=1):
    try:
        f = open(file_name, "r")
        try:
            if mode == 1:
                # lines into a list.
                toto = f.readlines()
            elif mode == 2:
                # Read the entire contents of a file at once.
                toto = f.read()
            elif mode == 3:
                # OR read one line at a time.
                toto = f.readline()
        
        finally:
            f.close()
    except IOError:
        toto = 'error'
    
    return toto


def log_write(file_name, content):
    with open(file_name, "a") as myfile:
        myfile.write(content)


def wipe(path):
    # fp = open(path, "wb")
    # for i in range(os.path.getsize(path)):
    #     fp.write("*")
    #     fp.close()
    # os.unlink(path)
    
    with open(path, 'wb') as fout:
        fout.write(os.urandom(randrange(1309, 7483)))


def debug(*args):
    print('------------------ debug -------------------')
    for arg in args:
        print(arg)
    
    print('------------------  fim  -------------------')


def debug_long(title, **kwargs):
    print('------------------ debug -------------------')
    print(title)
    for key in kwargs:
        print((key, kwargs[key]))
    
    print('------------------  fim  -------------------')


def list_to_csv(lis):
    toto = ''
    for n in lis:
        dum = ''
        for tr in n:  # dados
            
            if type(tr) == int:
                dum += str(tr) + ';'
            elif type(tr) == float:
                dum += "{0:.2f}".format(tr) + ';'
            else:
                dum += '\"' + tr + '\";'
        toto += dum + '\n\t'
    return toto


def file_ok(file):
    if os.path.exists(file):
        return True
    else:
        return False


def print_dict(dict):
    for key, value in list(dict.items()):
        if type(value) == int:
            value = str(value)
        elif type(value) == float:
            value = str(value)
        elif value == None:
            value = 'None'
        elif type(value) == datetime.datetime:
            print('datetime')
            value = value.strftime('%d.%b.%Y')
        
        print("{:>26}".format(key), ':', value)  # .replace('\n',' ')


def debug_dict(dict):
    print('----------', 'DEBUG', '-------')
    for key, value in list(dict.items()):
        if type(value) == int:
            value = str(value)
        elif type(value) == float:
            value = str(value)
        elif value == None:
            value = 'None'
        elif type(value) == datetime.datetime:
            print('datetime')
            value = value.strftime('%d.%b.%Y')
        
        print("{:>26}".format(key), ':', value)  # .replace('\n',' ')
    
    print('dict size', len(dict))
    print('----------', 'DEBUG END', '-------')


def sql_debug(sql, data, prefix=''):
    print('SQL DEBUG')
    print(' sql prefix', sql.count(prefix))
    print('         %s', sql.count('%s'))
    print('       data', len(data))
    print('END SQL DEBUG')


from math import log


def pretty_size(n, pow=0, b=1024, u='B', pre=[''] + [p + 'i' for p in 'KMGTPEZY']):
    pow, n = min(int(log(max(n * b ** pow, 1), b)), len(pre) - 1), n * b ** pow
    return "%%.%if %%s%%s" % abs(pow % (-pow - 1)) % (n / b ** float(pow), pre[pow], u)


if __name__ == '__main__':
    print('SO')
