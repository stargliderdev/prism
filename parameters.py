#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import os

WAN = False
dsPendentes = ''
ds_tecnicos = []
dsMeios = []
dsMeiosDic = {}
dsClasses = []
dsClassesDic = {}
ca_status = []
canned_msg_sms = []
dsSoftwareVersions = []
dsActividades = []
dsActividadesDic = {}
ds_areas = []
current_unit = ''
error_list = ''
unidade_id = 0
ass_status_txt = ''
ass_montante = 0
pendente = ''
ass_facturado = ''
os_version = []
isp_dict = {}
isp = []
dbms = []
dbms_dict = {}
hardware_types = []
un_status = []
un_status_dict = {}
hw_status = []
hw_status_dict = {}
ass_relatorio_interno = 0
brands = []
brands_dict = {}
models_dict = {}
brand_name = ''
supplier = ''
supplier_doc = ''
data_supplier_doc = datetime.datetime(2012, 1, 1)
hardware_un_add = False
db_host = '192.168.0.98'
db_port = '5432'
db_user = 'root'
db_password = 'masterkey'
DEVELOP = True
VERSION = '2020.12.10'
version = 18
if DEVELOP:
    db_host = '192.168.0.250'
db_database = 'prism'
dsSoftType = {}
ds_soft_type_dict = {}
commit_types = {}
conn_string = "host=" + db_host + " dbname=" + db_database + " port=" + db_port + " user=" + db_user + " password=" + db_password
brand_id = -1
un_ftypes = []
un_ftypes_dic = {}
unit_file_path = str(os.getcwd()) + '\\'
user_dict = {}
PRODUCTION_VERSION = '2020.1'
file1 = ('espiridiao@infornash.pt', 'O&!y7A?HZr6q$tZX', 'ftp.infornash.pt')
unit_dict = {}
motif_block = []
insoft_comercial_version = []
proc_dict = {'proc_date': datetime.datetime.now(),
             'proc_reported': '',
             'proc_action_report': '',
             'proc_serial_number': '',
             'proc_report_invoice': '',
             'proc_model': '',
             'proc_contacto': '',
             'proc_status': 'Resolvido',
             'proc_meio': 'Telefone',
             'proc_duracao': datetime.timedelta(hours=0, minutes=0, seconds=59),
             'proc_quem': '',
             'proc_unit_name': '',
             'proc_tecnico': 'Todos',
             'proc_updated': datetime.datetime.now(),
             'proc_nivel': 'Normal',
             'proc_montante': 0,
             'proc_jusante': 0,
             'proc_asterisk': '',
             'proc_pendente': False,
             'proc_facturar': False,
             'proc_facturado': '',
             'proc_data_fim': datetime.datetime.now() + datetime.timedelta(minutes=4),
             'proc_tags': '',
             'proc_relatorio_cliente': '',
             'proc_area': '',
             'proc_type': '0000',
             'proc_user': ''}
date_time_stack=''
client_sort_dict = {0: 'cl_nome ', 1: 'cl_id', 2: 'cl_localidade', 3: 'cl_cc DESC'}
proc_type = ['Todos']
proc_type_show = []
proc_sources = []
asterisk_stack_call = {}
canned_msg_mail = []
