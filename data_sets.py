#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import psycopg2

import psycopg2.extras
import parameters as gl
import libpg as libpg
import smtpmail


def conta_to_dict(index):
    conn = psycopg2.connect(gl.conn_string)
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = '''select contas.*,master.*
        from contas,master
        where ct_id = %s and ct_master_id = ma_id;'''
    dict_cur.execute(sql, (index,))
    rec = dict_cur.fetchone()
    dict_cur.close()
    conn.close()
    return rec


def unit_to_dic(index):
    conn = psycopg2.connect(gl.conn_string)
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = '''SELECT *
        FROM unidades, unit_type,clientes, areas
        WHERE un_id = %s and
        unit_type.un_type_id=unidades.un_type and
        un_cliente_id=cl_id and
        un_area=area_id;'''
    dict_cur.execute(sql, (index,))
    rec = dict_cur.fetchone()
    dict_cur.close()
    conn.close()
    return rec


def model_to_dict(index):
    conn = psycopg2.connect(gl.conn_string)
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = '''SELECT md_id, md_name, md_ref_oem, md_ref_gc,md_tags, br_name, hw_type_name,md_lifespan
            FROM models, brands, hardware_types
            where md_id = %s
            and models.md_brand_id = brands.br_id and md_hardware_type=hw_type_id'''
    dict_cur.execute(sql, (index,))
    rec = dict_cur.fetchone()
    dict_cur.close()
    conn.close()
    return rec


def master_to_dict(index):
    conn = psycopg2.connect(gl.conn_string)
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = 'SELECT master.*\
        FROM master\
        WHERE ma_id = %s ;'
    dict_cur.execute(sql, (index,))
    rec = dict_cur.fetchone()
    dict_cur.close()
    conn.close()
    return rec


def assistencia_to_dict(index):
    conn = psycopg2.connect(gl.conn_string)
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = 'select * from assistencias where proc_id = %s;'
    dict_cur.execute(sql, (index,))
    rec = dict_cur.fetchone()
    dict_cur.close()
    conn.close()
    return rec


def process_to_dict(index):
    conn = psycopg2.connect(gl.conn_string)
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = '''select *
             from assistencias
             inner join unidades on un_id=proc_unit_id
             inner join clientes on cl_id=unidades.un_cliente_id
             inner join proc_types on proc_type = proc_type_key
             where proc_id =  %s;'''
    dict_cur.execute(sql, (index,))
    rec = dict_cur.fetchone()
    dict_cur.close()
    conn.close()
    return rec


def hardware_to_dict(hw_id):
    conn = psycopg2.connect(gl.conn_string)
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = '''SELECT hw_unit_id,hw_model_id,hwd_status_id,hw_function,hw_id,hw_invoice,hw_invoice_date,hw_invoice_supplier,hw_sn,hw_supplier,hw_supplier_date,
     hw_supplier_warranty,hw_warranty,md_name,md_id,md_ref_gc,md_ref_oem,br_id,hw_obs, br_name,
     hwd_status_name as hw_status_name, br_name || ' ' || models.md_name as md_name, un_nome, hw_type_name
          FROM hardware, hw_status, models, brands, unidades, hardware_types
          WHERE hw_id = %s AND
          hw_status_id = hw_status.hwd_status_id AND
          hw_model_id = models.md_id AND
          models.md_brand_id = brands.br_id AND
          hardware_types.hw_type_id = md_hardware_type AND
           hardware.hw_unit_id = unidades.un_id;'''
    
    dict_cur.execute(sql, (hw_id,))
    rec = dict_cur.fetchone()
    dict_cur.close()
    conn.close()
    return rec


def licence_to_dict(software_id):
    conn = psycopg2.connect(gl.conn_string)
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = '''SELECT
              sf_id, sft_software , sf_date_contract,sf_date_valid,
              (case when software.sf_active = True then 'Activo '
                else
                    'Inactivo'
                end) as status, software.sf_lic_type,
                software.sf_lic_json, software.sf_version,sf_json_version
                FROM
                  software, software_type
                WHERE
                  software.sf_id = %s and
                  software.sf_version = software_type.sft_id '''
    dict_cur.execute(sql, (software_id,))
    rec = dict_cur.fetchone()
    dict_cur.close()
    conn.close()
    return rec


def eorder_to_dict(eorder_id):
    conn = psycopg2.connect(gl.conn_string)
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = '''select mo_options_json
            from modules
            where mo_id=%s '''
    dict_cur.execute(sql, (eorder_id,))
    rec = dict_cur.fetchone()
    dict_cur.close()
    conn.close()
    return rec


def canned_msg_to_dict(canned_name):
    conn = psycopg2.connect(gl.conn_string)
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = '''select *
            from msg_canned
            where lower(canned_name)=%s '''
    dict_cur.execute(sql, (canned_name.lower(),))
    rec = dict_cur.fetchone()
    dict_cur.close()
    conn.close()
    return rec



def get_ds_classes():
    a = libpg.query_many('select cl_id, cl_nome from classes order by cl_sort')
    gl.dsClasses = []
    gl.dsClassesDic = {}
    for n in a.output:
        gl.dsClasses.append(n[1])


def get_canned_messages_sms():
    a = libpg.query_many('SELECT canned_id, canned_name FROM msg_canned WHERE canned_type= %s ', (1,))
    gl.canned_msg_sms = []
    for n in a:
        gl.canned_msg_sms.append(n[1])


def get_canned_messages_mail():
    a = libpg.query_many('SELECT canned_id, canned_name FROM msg_canned WHERE canned_type= %s ', (2,))
    gl.canned_msg_mail = []
    for n in a:
        gl.canned_msg_mail.append(n[1])

def get_ds_software_type():
    a = libpg.query_many('select sft_id, sft_software from software_type where sft_active= %s order by sft_sort',
                         (True,))
    gl.dsSoftType = []
    gl.ds_soft_type_dict = {}
    gl.dsSoftTypeReversDic = {}
    for n in a:
        gl.dsSoftType.append(n[1])
        gl.ds_soft_type_dict[n[0]] = n[1]


def get_params():
    conn = psycopg2.connect(gl.conn_string)
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = '''select version from params where pr_id=1'''
    dict_cur.execute(sql, (True,))
    rec = dict_cur.fetchone()
    gl.ds_params = rec


def get_ds_assistencias():
    # print 'get get_ds_assistencias'
    
    gl.dsPendentes = []
    gl.dsPendentesDic = {}
    for n in libpg.query_many('select pe_id, pe_nome from pendentes order by pe_id', (True,)):
        gl.dsPendentes.append(n[1])
    gl.dsResolvidos = []
    gl.dsResolvidosDic = {}
    for n in libpg.query_many('select re_id, re_nome from resolvidos order by re_id'):
        gl.dsResolvidos.append(n[1])


def get_ds_tecnicos():
    gl.ds_tecnicos = []
    for n in libpg.query_many('select  tc_descricao from tecnicos order by tc_id'):
        gl.ds_tecnicos.append(n[0])


def get_ds_areas():
    gl.ds_areas = []
    a = libpg.query_many('select area_name from areas  order by area_name')
    for n in a:
        gl.ds_areas.append(n[0])


def get_comercial_version():
    gl.ds_areas = []
    a = libpg.query_many('select insoft_opt_name  from insoft_opt where insoft_opt_level=1 order by insoft_opt_order')
    for n in a:
        gl.insoft_comercial_version.append(n[0])


def get_ds_falhas():
    a = libpg.query_many('select fa_id, fa_nome from falhas order by fa_id')
    gl.dsFalhas = []
    for n in libpg.query_many('select fa_id, fa_nome from falhas order by fa_id'):
        gl.dsFalhas.append(n[1])


def get_ds_meios():
    gl.dsMeios = []
    # gl.dsMeiosDic = {}
    for n in libpg.query_many('select me_id, me_nome, me_action from meios order by me_id'):
        gl.dsMeios.append(n[1])


def get_ds_status():
    # case status
    gl.ca_status = ['Todos']
    # gl.ca_statusDic = {}
    for n in libpg.query_many('select st_id, st_descricao, st_action from status order by st_sort,st_descricao'):
        gl.ca_status.append(n[1].strip())


def get_ds_software_versions():
    gl.dsSoftwareVersions = []
    for n in libpg.query_many('select sversion_id, sversion_name from software_version order by sversion_id'):
        gl.dsSoftwareVersions.append(n[1])


def get_unit_types():
    a = libpg.sql_query('SELECT un_type_id, un_type_name from unit_type where un_type_active=True order by un_type_id')
    names = []
    un_dic = {}
    for n in a:
        names.append(n[1].strip())
        un_dic[n[1]] = n[0]
    return names, un_dic


# def getDsActividades():
#     a = libpg.query_many('SELECT ac_id, ac_nome from actividades order by ac_nome')
#     gl.dsActividades = []
#     gl.dsActividadesDic = {}
#     for n in a.output:
#         gl.dsActividades.append(n[1])
#         gl.dsActividadesDic[n[1]] = n[0]


def get_ds_brands():
    a = libpg.query_many('SELECT br_id, br_name from brands WHERE brands.br_active=TRUE order by br_name')
    gl.brands = ['Todas']
    for n in a:
        gl.brands.append(n[1])


def get_hardware_types():
    a = libpg.query_many('SELECT hw_type_id, hw_type_name from hardware_types order by hw_type_order')
    gl.hardware_types = []
    for n in a:
        gl.hardware_types.append(n[1])


def get_os():
    a = libpg.query_many('SELECT os_id, os_version from os_version order by os_order')
    gl.os_version = []
    for n in a:
        gl.os_version.append(n[1])


def get_isp():
    a = libpg.query_many('SELECT isp_id, isp_name from isp order by isp_name')
    gl.isp = []
    gl.isp_dict = {}
    for n in a:
        gl.isp.append(n[1])
        gl.isp_dict[n[1]] = n[0]


def get_un_status():
    a = libpg.query_many('SELECT un_status_id, un_status_name from un_status order by un_status_name')
    gl.un_status = []
    gl.un_status_dict = {}
    
    for n in a:
        gl.un_status.append(n[1])
        gl.un_status_dict[n[1]] = n[0]


def get_hw_status():
    a = libpg.query_many('SELECT hwd_status_id, hwd_status_name from hw_status order by hwd_status_id')
    gl.hw_status = []
    gl.hw_status_dict = {}
    for n in a:
        gl.hw_status.append(n[1])
        gl.hw_status_dict[n[1]] = n[0]


def get_commit_types():
    hl = libpg.sql_query('''SELECT *
        FROM comit_types;''')
    gl.commit_types = {}
    for n in hl:
        gl.commit_types[n[0]] = n


def get_dbms(unit_type):
    a = libpg.query_many('''SELECT db_id, db_edition from dbms
    and substring(sft_unit_type from ''' + str(unit_type) + ''' for 1) = '1' order by db_order''')
    gl.dbms = []
    gl.dbms_dict = {}
    for n in a:
        gl.dbms.append(n[1])


def get_unit_files_types():
    a = libpg.query_many('SELECT un_ftype_id, un_ftype_name from unit_files_types order by un_ftype_order')
    gl.un_ftypes = []
    gl.un_ftypes_dic = {}
    for n in a:
        gl.un_ftypes.append(n[1])
        gl.un_ftypes_dic[n[1].lower()] = n[0]


def get_model_data(a):
    sql = ('select md_id,\n'
           '        (select br_name from brands  where br_id =(select md_brand_id\n'
           '        from models where md_id = (select hw_model_id from hardware where hw_id= %s))),md_name\n'
           '        from models where md_id = (select hw_model_id from hardware where hw_id= %s)')
    hl = libpg.query_one(sql, (a, a))
    return {'md_id': hl[0], 'br_name': hl[1], 'md_name': hl[2]}


def log_entry(unit, entry):
    sql = 'UPDATE unidades set un_log =%s' + ' || un_log where un_id=%s'
    libpg.execute_query(sql, (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' : ' + entry + '\n', unit))


def get_user_data(u_name, u_pin):
    sql = 'select * from users where user_name=%s and user_pin=%s'
    conn = psycopg2.connect(gl.conn_string)
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    dict_cur.execute(sql,(u_name, u_pin))
    rec = dict_cur.fetchone()
    dict_cur.close()
    conn.close()
    return rec
    
    



if __name__ == "__main__":
    pass
