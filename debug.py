#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime


def debug_long(title,**kwargs):
    print('------------------ debug -------------------')
    print(title)
    for key in kwargs:
        print((key, kwargs[key]))

    print('------------------  fim  -------------------')

def debug_var_1(**kwargs):
    for name, value in list(kwargs.items()):
        print(name, value)


def debug_var(arg):
    import inspect
    import re
    frame = inspect.currentframe()
    try:
        context = inspect.getframeinfo(frame.f_back).code_context
        caller_lines = ''.join([line.strip() for line in context])
        m = re.search(r'echo\s*\((.+?)\)$', caller_lines)
        if m:
            caller_lines = m.group(1)
        print('-------- DEBUG VAR ------')
        print(caller_lines[15:], arg)   #, type(caller_lines)
        print('------ DEBUG VAR END-----')

    finally:
        del frame

def debug_sql(sql, data):
    import datetime
    x = sql.find(')')
    a = sql[sql.find('(')+1:x]
    b = sql[x+1:sql.find(')',x+1)]

    b = b.split(',')
    a = a.split(',')
    print('-------------')
    print('SQL', len(a), 'DATA',len(data))
    print()
    if len(a)!= len(b):
        print()
        print('Erro de index', 'Campos:',len(a),'Dicionario:', len(b))
        sys.exit(1)
    for n in range(0,len(a)):
        if type(data[n]) == datetime.datetime:
            vlue = data[n].strftime("%b %d %Y %H:%M:%S")
        else:
            vlue = data[n]
        print("{0:<25}".format(a[n].strip()),"{0:^4}".format(b[n].strip()),"{0:<40}".format(vlue))

def print_dataset(data_set):
    col = len(data_set[0])-1
    for n in data_set:
        for f in range(0,col):
            print(n[f], end=' ')
        print()


def debug_dict(dict):
    print('----------','DEBUG','-------')
    for key, value in list(dict.items()) :
        if type(value) == int:
            value = str(value)
        elif type(value) == float:
            value = str(value)
        elif value == None:
            value = 'None'
        elif type(value) == datetime.datetime:
            print('datetime')
            value = value.strftime('%d.%b.%Y')

        print("{:>26}".format(key),':', value) #.replace('\n',' ')

    print('dict size', len(dict))
    print('----------','DEBUG END','-------')


def dict_to_code(di):
    for key, value in list(di.items()) :
        # self.pop_control(self.inactive,a['inactive'])
        print(' self.pop_control(self.'+key+',a[\'' + key + '\'])')

def print_record(rec):
    col = len(rec)-1
    for f in range(0,col):
        print(rec[f], end=' ')
    print()

    # debug = QPushButton('larguras')
    # self.connect(debug, SIGNAL("clicked()"), self.call_debug)
    # mainTabLayout.addWidget(debug)
    # mainTabLayout.addStretch()