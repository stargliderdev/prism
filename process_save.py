#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import parameters as gl
import libpg as libpg


def save_process(data_dict):
    flag = True
    if not data_dict['proc_tecnico'] in data_dict:
        flag = False
    data_dict['proc_unit_name'] = gl.unit_dict['un_name']
    data_dict['proc_unit_id'] = gl.unit_dict['un_id']
    data_dict['proc_updated'] = datetime.datetime.now()
    data_dict['proc_area'] = gl.unit_dict['un_area']
    data_dict['proc_user'] = gl.user_dict['user_name']
    if flag:
        return False, -1
    else:
        sql = '''insert into assistencias  (
           proc_date,
           proc_unit_id,
           proc_reported,
           proc_action_report,
           proc_serial_number,
           proc_report_invoice,
           proc_model,
           proc_contacto,
           proc_status,
           proc_meio,
           proc_duracao,
           proc_quem,
           proc_unit_name,
           proc_tecnico,
           proc_updated,
           proc_nivel,
           proc_montante,
           proc_jusante,
           proc_asterisk,
           proc_pendente,
           proc_facturar,
           proc_facturado,
           proc_data_fim,
           proc_tags,
           proc_relatorio_cliente,
           proc_area,
           proc_type,
           proc_user,
           proc_source,
           proc_cause_report)
           values(%s,%s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        data = (
            data_dict['proc_date'],
            data_dict['proc_unit_id'],
            data_dict['proc_reported'],
            data_dict['proc_action_report'],
            data_dict['proc_serial_number'],
            data_dict['proc_report_invoice'],
            data_dict['proc_model'],
            data_dict['proc_contacto'],
            data_dict['proc_status'],
            data_dict['proc_meio'],
            data_dict['proc_duracao'],
            data_dict['proc_quem'],
            data_dict['proc_unit_name'],
            data_dict['proc_tecnico'],
            data_dict['proc_updated'],
            data_dict['proc_nivel'],
            data_dict['proc_montante'],
            data_dict['proc_jusante'],
            data_dict['proc_asterisk'],
            data_dict['proc_pendente'],
            data_dict['proc_facturar'],
            data_dict['proc_facturado'],
            data_dict['proc_data_fim'],
            data_dict['proc_tags'],
            data_dict['proc_relatorio_cliente'],
            data_dict['proc_area'],
            data_dict['proc_type'],
            data_dict['proc_user'],
            data_dict['proc_source'],
            data_dict['proc_cause_report'])
    
        libpg.execute_query(sql, data)
        process_number = libpg.query_one('select max(proc_id) as max_id from assistencias', (True,))[0]
        if data_dict['proc_montante'] > 0:
            libpg.execute_query('''UPDATE assistencias set proc_pendente = False, proc_jusante = %s
                         where proc_id = %s''', (process_number, data_dict['proc_montante']))
        return True,process_number
    

def intervention(data_dict):
    sql = '''INSERT into assistencias (PROC_DATE,
    PROC_UPDATED, PROC_UNIT_ID, PROC_TECNICO, proc_action_report,
                  PROC_QUEM,proc_contacto,
                  proc_meio,proc_duracao,proc_unit_name,
                  proc_reported, proc_montante, proc_jusante, proc_status, proc_nivel,proc_facturar,proc_pendente, proc_data_fim, proc_type, proc_user)
                values (%s,%s,%s,%s,%s,%s,'',%s,%s,%s,%s,0,-1,'Aguarda n/ Intervenção', 'Normal', False,True, %s,%s,%s)'''
    data = (datetime.datetime.now(),
            datetime.datetime.now(),
            gl.unit_dict['un_id'],
            data_dict['tech'],
            data_dict['problem'],
            data_dict['client_name'],
            'Escritorio',
            datetime.timedelta(hours=0, minutes=0, seconds=59),
            gl.unit_dict['un_name'],
            'Erro nas comunicações',
            datetime.datetime.now() + datetime.timedelta(minutes=4), data_dict['proc_type'],gl.user_dict['user_name']
            )
    libpg.execute_query(sql, data)
    process_number = libpg.query_one('select max(proc_id) as max_id from assistencias', (True,))[0]
    
    return process_number


def ticket(data_dict):
    sql = '''INSERT into assistencias (proc_date,proc_updated,proc_unit_id,proc_tecnico,proc_action_report,
                  proc_serial_number,proc_report_invoice,proc_quem,proc_model,proc_contacto, proc_meio,proc_duracao,proc_unit_name,
                  proc_reported, proc_montante, proc_jusante,proc_asterisk, proc_status, proc_nivel,proc_facturar,proc_pendente,proc_facturado, proc_data_fim,
                  proc_user, proc_cause_report,proc_internal_report,proc_type,proc_source)
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s,%s)'''
    data = (data_dict['proc_date'],
            data_dict['proc_updated'],
            data_dict['proc_unit_id'],
            data_dict['proc_tecnico'],
            data_dict['proc_action_report'],
            data_dict['proc_serial_number'],
            data_dict['proc_report_invoice'],
            data_dict['proc_quem'],
            data_dict['proc_model'],
            data_dict['proc_contacto'],
            data_dict['proc_meio'],
            data_dict['proc_duracao'],
            data_dict['proc_unit_name'],
            data_dict['proc_reported'],
            data_dict['proc_montante'],
            data_dict['proc_jusante'],
            data_dict['proc_asterisk'],
            data_dict['proc_status'],
            data_dict['proc_nivel'],
            data_dict['proc_facturar'],
            data_dict['proc_pendente'],
            data_dict['proc_facturado'],
            data_dict['proc_data_fim'],
            gl.user_dict['user_name'],
            data_dict['proc_cause_report'],
            data_dict['proc_internal_report'],
            data_dict['proc_type'],
            data_dict['proc_source'])
    libpg.execute_query(sql, data)
    
    num_pedido = libpg.query_one('select max(proc_id) as max_id from assistencias', (True,))[0]
    """ fecha o proc a montante se houver i não for INFO"""
    if data_dict['proc_montante'] > 0 and data_dict['proc_type'] != 'INFO':
        libpg.execute_query('''UPDATE assistencias set proc_pendente = False, proc_jusante = %s
                     where proc_id = %s''', (num_pedido,data_dict['proc_montante']))

    return num_pedido


if __name__ == '__main__':
    pass
