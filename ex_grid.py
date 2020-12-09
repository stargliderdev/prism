#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.Qt import Qt
from PyQt5.QtGui import QColor, QBrush, QFont
from PyQt5.QtWidgets import QHBoxLayout, QCheckBox, QWidget, QComboBox, QTableWidgetItem

import qlib


def ex_grid_update(grid_ctrl, col, data=[], refresh=False, hidden=-1, nulls=False):
    def format_as_integer(d):
        # d = dado
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        item.setText(str(d))
        return item
    
    def format_as_string(d):
        # d = dado
        item = QTableWidgetItem()
        item.setText(d)
        return item
    
    def format_as_date(d):
        # d = dado
        item = QTableWidgetItem()
        item.setText(d.strftime('%d.%b.%Y'))
        return item
    
    def format_as_string_center(d):
        # d = dado
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignCenter)
        item.setText(d)
        return item
    
    def format_as_null():
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignCenter)
        item.setText('null')
        return item
    
    headers = []
    col_type = []
    for k, v in col.items():
        # print v
        headers.append(v[0])
        col_type.append(v[1])
    colCount = len(headers)
    
    if not refresh:
        grid_ctrl.clear()
        grid_ctrl.setColumnCount(colCount)
        grid_ctrl.setHorizontalHeaderLabels(headers)
    
    grid_ctrl.setRowCount(0)
    grid_ctrl.setRowCount(len(data))
    lin = 0
    for n in data:
        for f in range(0, len(n)):
            if n[f] is None:
                if nulls:
                    grid_ctrl.setItem(lin, f, format_as_null())
            else:
                if col_type[f] == 'i':
                    # print 'int'
                    grid_ctrl.setItem(lin, f, format_as_integer(n[f]))
                elif col_type[f] == 'd':  # date
                    grid_ctrl.setItem(lin, f, format_as_date(n[f]))
                elif col_type[f] == 's':
                    grid_ctrl.setItem(lin, f, format_as_string(n[f]))
                elif col_type[f] == 'sc':
                    grid_ctrl.setItem(lin, f, format_as_string_center(n[f]))
        
        lin += 1
    if hidden > -1:
        grid_ctrl.hideColumn(hidden)
    # if not refresh:
    #     grid_ctrl.resizeColumnsToContents()


def ex_grid__ctrl_update(grid_ctrl, col_dict, data=[], options=[]):
    def format_as_integer(d):
        # d = dado
        item = QTableWidgetItem()
        
        item.setTextAlignment(Qt.AlignRight)
        item.setText(str(d))
        return item
    
    def format_as_string(d):
        item = QTableWidgetItem()
        item.setText(d)
        return item
    
    def format_as_date(d):
        item = QTableWidgetItem()
        item.setText(d.strftime('%d.%b.%Y'))
        return item
    
    def format_as_string_center(d):
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignCenter)
        item.setText(d)
        return item
    
    number_of_columns = len(col_dict)
    headers = []
    col_type = []
    field_index = {}
    for k, v in col_dict.items():
        # print v
        headers.append(v[0])
        col_type.append(v[1])
        field_index[k] = v[2]
    colCount = len(headers)
    grid_ctrl.clear()
    grid_ctrl.setColumnCount(colCount)
    grid_ctrl.setHorizontalHeaderLabels(headers)
    grid_ctrl.setRowCount(0)
    grid_ctrl.setRowCount(len(data))
    lin = 0
    for n in data:
        for f in range(0, number_of_columns):
            if col_type[f] == 'i':
                # print 'int'
                grid_ctrl.setItem(lin, f, format_as_integer(n[field_index[f]]))
            elif col_type[f] == 'd':  # date
                grid_ctrl.setItem(lin, f, format_as_date(n[field_index[f]]))
            elif col_type[f] == 's':
                grid_ctrl.setItem(lin, f, format_as_string(n[field_index[f]]))
            elif col_type[f] == 'sc':
                grid_ctrl.setItem(lin, f, format_as_string_center(n[field_index[f]]))
            elif col_type[f] == 'xb':  # checkbox
                # grid_ctrl.setItem(lin, ' ', QCheckBox())
                grid_ctrl.setCellWidget(lin, f, qlib.checkBoxGrid())
        lin += 1
    grid_ctrl.resizeColumnsToContents()


def insert_row(grid_ctrl, data=[], data_type=[]):
    grid_ctrl.setRowCount(grid_ctrl.rowCount() + 1)
    if not data == []:
        lin = grid_ctrl.rowCount() - 1
        for n in range(0, len(data)):
            # print data[n],data_type[n],n
            if data[n] is None:
                grid_ctrl.setItem(lin, n, format_as_null())
            else:
                if data_type[n] == 'd5r':
                    grid_ctrl.setItem(lin, n, format_as_decimal5r(data[n]))
                elif data_type[n] == 'd2r':
                    grid_ctrl.setItem(lin, n, format_as_decimal2r(data[n]))
                elif data_type[n] == 'd5':
                    grid_ctrl.setItem(lin, n, format_as_decimal5(data[n]))
                elif data_type[n] == 'd3':
                    grid_ctrl.setItem(lin, n, format_as_decimal3(data[n]))
                elif data_type[n] == 'i':
                    grid_ctrl.setItem(lin, n, format_as_integer(data[n]))
                elif data_type[n] == 'ir':
                    grid_ctrl.setItem(lin, n, format_as_integer_ro(data[n]))
                elif data_type[n] == 'd':  # date
                    grid_ctrl.setItem(lin, n, format_as_date(data[n]))
                elif data_type[n] == 's':
                    grid_ctrl.setItem(lin, n, format_as_string(data[n]))
                elif data_type[n] == 'sr':
                    grid_ctrl.setItem(lin, n, format_as_string_ro(data[n]))
                elif data_type[n] == 'sc':
                    grid_ctrl.setItem(lin, n, format_as_string_center(data[n]))
                elif data_type[n] == 'cb':
                    grid_ctrl.setCellWidget(lin, n, comboBoxGrid())
                elif data_type[n] == 'f2':
                    grid_ctrl.setItem(lin, n, format_as_float2(data[n]))
                elif data_type[n] == 'f2r':
                    grid_ctrl.setItem(lin, n, format_as_float2r(data[n]))


def checkBoxGrid(label=''):
    w = QWidget()
    l = QHBoxLayout(w)
    l.setContentsMargins(0, 0, 0, 0)
    l.addStretch()
    c = QCheckBox(label)
    l.addWidget(c)
    l.addStretch()
    return w


def comboBoxGrid():
    w = QWidget()
    l = QHBoxLayout(w)
    l.setContentsMargins(0, 0, 0, 0)
    l.addStretch()
    c = QComboBox()
    c.addItems(['cx6', 'cx12', 'cx24'])
    l.addWidget(c)
    l.addStretch()
    return w


def format_as_decimal3(d):
    # d = dado
    item = QTableWidgetItem()
    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    if d < 0:
        item.setTextColor(QColor(Qt.red))
    item.setText(str("%.3f" % round(d, 3)))
    return item


def format_as_decimal2(d):
    # d = dado
    item = QTableWidgetItem()
    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    item.setText(str("%.2f" % round(d, 2)))
    return item


def format_as_decimal2r(d):
    # d = dado
    item = QTableWidgetItem()
    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    item.setFlags(Qt.ItemIsEnabled)
    if d < 0:
        item.setTextColor(QColor(Qt.red))
    else:
        item.setTextColor(QColor(Qt.blue))
    item.setText(str("%.2f" % round(d, 2)))
    return item


def format_as_decimal5(d):
    # d = dado
    item = QTableWidgetItem()
    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    item.setText(str("%.5f" % round(d, 5)))
    return item


def format_as_decimal5r(d):
    # d = dado
    item = QTableWidgetItem()
    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    item.setFlags(Qt.ItemIsEnabled)
    if d < 0:
        item.setTextColor(QColor(Qt.red))
    else:
        item.setTextColor(QColor(Qt.blue))
    item.setText(str("%.5f" % round(d, 5)))
    return item


def format_as_integer(d):
    # d = dado
    item = QTableWidgetItem()
    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    item.setText(str(d))
    return item


def format_as_integer_ro(d):
    # d = dado
    item = QTableWidgetItem()
    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    item.setFlags(Qt.ItemIsEnabled)
    item.setText(str(d))
    return item


def format_as_string(d):
    # d = dado
    item = QTableWidgetItem()
    item.setText(d)
    return item


def format_as_string_ro(d):
    # d = dado
    item = QTableWidgetItem()
    item.setFlags(Qt.ItemIsEnabled)
    if d < 0:
        item.setTextColor(QColor(Qt.red))
    else:
        item.setTextColor(QColor(Qt.blue))
    item.setText(d)
    return item


def fs_left_ro(d):
    # d = dado
    bb = QBrush(QColor(Qt.lightGray))
    # bb.setColor(QColor(Qt.red))
    item = QTableWidgetItem()
    item.setBackground(bb)
    item.setFlags(Qt.ItemIsEnabled)
    item.setTextColor(QColor(Qt.blue))
    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    item.setText(d)
    return item


def fs_center_ro(d):
    item = QTableWidgetItem()
    item.setFlags(Qt.ItemIsEnabled)
    item.setTextColor(QColor(Qt.blue))
    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
    item.setText(d)
    return item


def format_as_float2(d):
    item = QTableWidgetItem()
    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    item.setText("%.2f" % d)
    return item


def format_as_float2r(d):
    item = QTableWidgetItem()
    item.setFlags(Qt.ItemIsEnabled)
    item.setTextColor(QColor(Qt.blue))
    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    item.setText("%.2f" % d)
    return item


def format_as_date(d):
    # d = dado
    item = QTableWidgetItem()
    item.setText(d.strftime('%d.%b.%Y'))
    return item


def format_as_timestamp(d):
    # d = dado
    item = QTableWidgetItem()
    item.setText(d.strftime('%d.%b.%Y %H:%M'))
    return item


def format_as_string_center(d):
    # d = dado
    item = QTableWidgetItem()
    item.setTextAlignment(Qt.AlignCenter)
    item.setText(d)
    return item


def format_as_null():
    item = QTableWidgetItem()
    item.setTextAlignment(Qt.AlignCenter)
    item.setText('null')
    return item


def f_empty():
    item = QTableWidgetItem()
    return item


def make_grid(grid_ctrl, headers, col_width):
    col_count = len(headers)
    grid_ctrl.clear()
    grid_ctrl.setColumnCount(col_count)
    grid_ctrl.setHorizontalHeaderLabels(headers)
    for k in col_width:
        grid_ctrl.setColumnWidth(k[0], k[1])


def grid_std(grid_ctrl, **kwargs):
    if kwargs is not None:
        if "data" in kwargs:
            if 'f_col' in kwargs:
                grid_ctrl.setColumnCount(len(kwargs['f_col']))
                if "add" in kwargs:
                    grid_ctrl.setRowCount(grid_ctrl.rowCount() + 1)
                    lin = grid_ctrl.rowCount() - 1
                else:
                    grid_ctrl.setRowCount(0)
                    grid_ctrl.setRowCount(len(kwargs['data']))
                    lin = 0
                for n in kwargs['data']:
                    for f in range(0, len(kwargs['f_col'])):
                        if n[f] is None:
                            grid_ctrl.setItem(lin, f, f_empty())
                        else:
                            if kwargs['f_col'][f] == 'i':
                                grid_ctrl.setItem(lin, f, format_as_integer(n[f]))
                            elif kwargs['f_col'][f] == 'd':
                                grid_ctrl.setItem(lin, f, format_as_date(n[f]))
                            elif kwargs['f_col'][f] == 't':
                                grid_ctrl.setItem(lin, f, format_as_timestamp(n[f]))
                            elif kwargs['f_col'][f] == 's':
                                grid_ctrl.setItem(lin, f, format_as_string(n[f]))
                            elif kwargs['f_col'][f] == 'sc':
                                grid_ctrl.setItem(lin, f, format_as_string_center(n[f]))
                            elif kwargs['f_col'][f] == 'd5r':
                                grid_ctrl.setItem(lin, f, format_as_decimal5r(n[f]))
                            elif kwargs['f_col'][f] == 'd2r':
                                grid_ctrl.setItem(lin, f, format_as_decimal2r(n[f]))
                            elif kwargs['f_col'][f] == 'd2':
                                grid_ctrl.setItem(lin, f, format_as_decimal2(n[f]))
                            elif kwargs['f_col'][f] == 'd5':
                                grid_ctrl.setItem(lin, f, format_as_decimal5(n[f]))
                            elif kwargs['f_col'][f] == 'd3':
                                grid_ctrl.setItem(lin, f, format_as_decimal3(n[f]))
                            elif kwargs['f_col'][f] == 'ir':
                                grid_ctrl.setItem(lin, f, format_as_integer_ro(n[f]))
                            elif kwargs['f_col'][f] == 'sr':
                                grid_ctrl.setItem(lin, f, format_as_string_ro(n[f]))
                            elif kwargs['f_col'][f] == 'cb':
                                grid_ctrl.setCellWidget(lin, n, comboBoxGrid())
                            elif kwargs['f_col'][f] == 'f2':
                                grid_ctrl.setItem(lin, f, format_as_float2(n[f]))
                            elif kwargs['f_col'][f] == 'f2r':
                                grid_ctrl.setItem(lin, f, format_as_float2r(n[f]))
                    lin += 1
            
            else:
                return False, 'no f_col'
        else:
            return False, 'no data'
    
    return (True,)


def grid_process_make_grid(ctrl_grid):
    ctrl_grid.setColumnCount(7)
    ctrl_grid.setHorizontalHeaderLabels(['ID', 'Unidade/Avaria', 'Data/Nivel', 'Estado', 'Localidade', 'Zona', 'un_id'])
    ctrl_grid.setRowCount(0)


def process_update_grid(ctrl_grid, data_set):
    if len(data_set) > 0: # tem de ter mais de zero linhas
        ctrl_grid.setRowCount(len(data_set)+1)
    else:
        ctrl_grid.setRowCount(0)
    linha = 0
    font = QFont()
    font.setBold(True)
    font.setWeight(75)
    for n in data_set:
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        item.setBackground(QBrush(QColor(0, 240, 0)))
        item.setFont(font)
        item.setText(str(n[0]))
        ctrl_grid.setItem(linha, 0, item)
        
        item = QTableWidgetItem()  # data
        ctrl_grid.setItem(linha, 2, item)
        item.setText(n[1])
        
        item = QTableWidgetItem() # estado
        item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
        ctrl_grid.setItem(linha, 1, item)
        item.setText(n[2])

        item = QTableWidgetItem()
        ctrl_grid.setItem(linha, 3, item)
        item.setText(n[3])
        item = QTableWidgetItem()
        ctrl_grid.setItem(linha, 4, item)
        item.setText(n[4])
        item = QTableWidgetItem()
        ctrl_grid.setItem(linha, 6, item)
        item.setText(str(n[6]))

        linha += 1  # new line
        
        item = QTableWidgetItem() # avaria
        item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
        ctrl_grid.setItem(linha, 1, item)
        item.setText(n[8])
        
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignRight | Qt.AlignTop)
        ctrl_grid.setItem(linha, 0, item)
        item.setText('└ ')
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
        ctrl_grid.setItem(linha, 2, item)
        item.setText(n[7])

        linha += 1
    ctrl_grid.resizeColumnsToContents()
    ctrl_grid.setColumnWidth(0, 100)
    ctrl_grid.setColumnWidth(1, 420)
    ctrl_grid.setColumnWidth(5, 0)
    ctrl_grid.setColumnWidth(6, 0)
    for n in range(0, ctrl_grid.rowCount()):
        ctrl_grid.resizeRowToContents(n)


if __name__ == '__main__':
    pass
