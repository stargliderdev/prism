#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import ex_grid
import libpg
import qlib as qc
import models_lib
import dateutil.parser as dparser


def correct_dates():
    sql = '''select cm_id,cm_value
          from comitments_unit
          where cm_act_id in (12,13,14,15,24) order by cm_id'''
    xl = libpg.query_many(sql)
    for n in xl:
        try:
            a = str(dparser.parse(n[1],fuzzy=True, dayfirst=True))
            print(n[0],n[1],' --->', a[:10])
            libpg.execute_query('''update comitments_unit set cm_value = %s where cm_id = %s''', (a[:10],n[0]))
        except ValueError:
            pass
        
        
correct_dates()

