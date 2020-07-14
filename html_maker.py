#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import parameters as gl
import smtpmail


def process_to_html(ass_dict):
    div_title = '''<div style="margin-bottom: 10px; margin-left: 10px;"><h3 class='round_title'>'''
    div_end = '''</h3></div>\n'''
    toto: str = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8">
                <style> .round_conner {color:#000000; font:14px verdana,sans-serif; display: inline;
                background:#56C5EA; height: 25px; border-radius: 7px; padding-left:10px; padding-right:10px;
                padding-bottom:3px; padding-top:2px; text-align:right; } .round_title {color:#000000;
                font:19px verdana,sans-serif; background:#56C5EA; height: 25px; border-radius: 7px;
                padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px; text-align:center;
                } .round_small {color:#FFDF00; font:14px verdana,sans-serif; display: inline; background:#6F4E37;6F4E37
                height: 25px; border-radius: 4px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px;
                text-align:right; } .round_tags {color:#ffffff; font:10px verdana,sans-serif; display: inline; background:#6FD000;
                height: 25px; border-radius: 4px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px;
                text-align:right; } .terminal {color:#00DD00; font:14px verdana,sans-serif; background-color:#000000; border-radius: 6px;
                padding-left:10px; padding-right:10px; padding-bottom:4px; padding-top:2px; text-align:left; }
                #label {border: solid #CCC 1.0pt;
                text-align: right; font-family: Verdana; font-size: 10px; color: #333; font-weight: bold; vertical-align: middle;
                height: 20px; width:100px  } </style> </head>'''
    td_caixa = '<tr><td id="label">'
    td_data = '<td style="color: #000080 ; font-family:Verdana; font-size:14px">'
    td_data_mono = '<td style="font-family: Menlo, Consolas, Monaco, monospace;">'
    td_end = '</td></tr>\n'
    toto += '<pre>'
    toto += '<b>         Tipo:</b> ' + ass_dict['proc_type'] + '<br>'
    toto += '<b>       Numero:</b> #' + str(ass_dict['proc_id']) + '<br>'
    toto += '<b>         Data:</b> ' + ass_dict['proc_date'].strftime("%d-%m-%Y %H:%M") + '<br>'
    toto += '<b>       N.I.F.:</b> ' + ass_dict['cl_nif'] + '<br>'
    toto += '<b>      Unidade:</b> ' + ass_dict['proc_unit_name'] + '<br>'
    toto += '<b>       Morada:</b> ' + ass_dict['un_morada'] + ', ' + ass_dict['un_localidade'] + '<br>'
    # toto += '<b>      C.P.:</b>' + td_data + ass_dict['un_cp'] + '<br>'
    toto += '</pre>'
    toto += ''' <table>'''
    if not ass_dict['proc_model'] == '':
        toto += td_caixa + 'Modelo:' + td_data + ass_dict['proc_model']
    if not ass_dict['proc_serial_number'] == '':
        toto += '<td id="label">' + 'Num. de Série:' + td_data + ass_dict['proc_serial_number'] + td_end
    toto += td_caixa + 'Problema:' + td_data + ass_dict['proc_reported'] + td_end
    toto += td_caixa + 'Relatório:' + td_data + ass_dict['proc_report_internal'].replace('\n', '<br>') + td_end
    toto += td_caixa + 'Meio:' + td_data + ass_dict['proc_meio'] + td_end
    toto += td_caixa + 'Origem:' + td_data + ass_dict['proc_meio'] + td_end
    if not ass_dict['proc_quem'] == '':
        toto += td_caixa + 'Contacto:' + td_data + ass_dict['proc_quem'] + ' ' + ass_dict['proc_contacto'] + td_end
    if not ass_dict['proc_report_invoice'] == '':
        toto += td_caixa + 'Relatório p/ Fac.:\n' + td_data + ass_dict['proc_report_invoice']
    toto += td_caixa + 'Duração:' + td_data + ass_dict['proc_duracao'].strftime("%H:%M") + td_end
    toto += td_caixa + 'Técnico:' + td_data + ass_dict['proc_tecnico'] + td_end
    toto += td_caixa + 'Estado:' + td_data + ass_dict['proc_status'] + td_end
    toto += ''' </table>'''
    toto += '''<pre>'''
    toto += '<b> Proprietário:</b>' + ass_dict['cl_nome'] + '<br>'
    toto += '<b>       N.I.F.:</b>' + ass_dict['cl_nif'] + '<br>'
    toto += '<b>       Morada:</b>' + ass_dict['cl_morada'] + '<br>'
    toto += '<b>    Sede C.P.:</b>' + ass_dict['cl_cp'] + '<br>'
    if ass_dict['cl_cc'] > 0:
        toto += '<b>  C. Corrente: <font color="red" >' + '{0:.2f}'.format(ass_dict['cl_cc']) + '</b></font><br>'
    else:
        toto += '<b>  C. Corrente:</b>' + '{0:.2f}'.format(ass_dict['cl_cc']) + '<br>'
   
    toto += '<b>     Recebido:</b>' + ass_dict['proc_user'] + '<br>'
    toto += '</html>'
    # print(toto, file=open("output.html", "a"))
    return toto


def process_to_html_mono(ass_dict):
    div_end = '''<br>\n'''
    toto: str = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8"><html>'''
    td_caixa = ''
    td_data = '<b>'
    td_end = '<br>\n'
    # toto += ''' <table>'''
    toto += '<font size="5px";><pre>'
    toto += ass_dict['proc_type'] + ' #' + str(ass_dict['proc_id']) + '/' + ass_dict['proc_date'].strftime ("%d-%m-%Y %H:%M") + div_end
    toto += '<b>   Unidade:</b>' + '<font color="blue" >' + ass_dict['proc_unit_name'] + '</font><br>'
    toto += '<b>  Problema:</b>' + ass_dict['proc_reported'] + '<br>'
    dum = ''
    for n in ass_dict['proc_report_internal'].split('\n'):
        dum += 12 * ' ' + n + '<br>'
    toto += '<b> Relatório:</b>' + '<mark>' + dum + '</mark>'
    toto += '<b>      Meio:</b>' + ass_dict['proc_meio'] + td_end
    if not ass_dict['proc_quem'] == '':
        toto += '<b>  Contacto:</b>' + ass_dict['proc_quem'] + ' ' + ass_dict['proc_contacto'] + td_end
    # toto += '<hr style="border: 1px dashed #C0C0C0" color="#FFFFFF" size="6">'
    if ass_dict['proc_duracao'].second == 00:
        toto += '<b>   Duração:</b>' + ass_dict['proc_duracao'].strftime("%H:%M") + td_end
    else:
        toto += '<b>   Duração:</b>' + ass_dict['proc_duracao'].strftime("%H:%M") + td_end
    toto += '<b>   Morada:</b>' + ass_dict['un_morada'] + td_end
    toto += '<b>Localidade:</b>' + ass_dict['un_localidade'] + td_end
    toto += '<b>C.P.:</b>' + ass_dict['un_cp'] #+ td_end
    # toto += '</table>\n'
    # toto += '<hr style="border: 1px dashed #C0C0C0" color="#FFFFFF" size="6">'
    # toto += ''' <table>'''
    toto += '<b>Proprietário:</b>' + ass_dict['cl_nome'] + td_end
    toto += '<b>N.I.F.:</b>' + ass_dict['cl_nif'] + td_end
    toto += '<b>Morada:</b>' + ass_dict['cl_morada'] + td_end
    toto += '<b>Sede C.P.:</b>' + ass_dict['cl_cp'] + td_end
    toto += '<b>C. Corrente:</b>' + '{0:.2f}'.format(ass_dict['cl_cc']) + td_end
    
    try:
        toto += '<b>Modelo:</b>' + ass_dict['proc_model']
    except TypeError:
        pass
    try:
        toto += '<b>Num. de Série:</b>' +  ass_dict['proc_serial_number'] + td_end
    except TypeError:
        pass
    try:
        toto += '<b>Relatório p/ Fac.:</b>' + ass_dict['proc_report_invoice']
    except (TypeError, AttributeError):
        pass
    if not ass_dict['proc_tecnico'] == '':
        toto += '<b>Técnico:</b>' + ass_dict['proc_tecnico'] + td_end
    else:
        toto += '<b>Técnico:<b>' + ass_dict['proc_user'].upper() + td_end
    toto += '<b>Recebido:<b>' + td_data + ass_dict['proc_user'] + td_end
    toto += '<b>Estado:<b>' + td_data + ass_dict['proc_status'] + td_end
    # toto += '</table>\n'
    toto += '</font></html>'
    print(toto)
    os.remove("output.html")
    print(toto, file=open("output.html", "a"))
    return toto


def block_to_html(ass_dict):
    div_title = '''<div style="margin-bottom: 10px; margin-left: 10px;"><h3 class='round_title'>'''
    div_end = '''</h3></div>\n'''
    toto: str = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8">
                <style> .round_conner {color:#000000; font:14px verdana,sans-serif; display: inline;
                background:#56C5EA; height: 25px; border-radius: 7px; padding-left:10px; padding-right:10px;
                padding-bottom:3px; padding-top:2px; text-align:right; } .round_title {color:#000000;
                font:19px verdana,sans-serif; background:#56C5EA; height: 25px; border-radius: 7px;
                padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px; text-align:center;
                } .round_small {color:#FFDF00; font:14px verdana,sans-serif; display: inline; background:#6F4E37;6F4E37
                height: 25px; border-radius: 4px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px;
                text-align:right; } .round_tags {color:#ffffff; font:10px verdana,sans-serif; display: inline; background:#6FD000;
                height: 25px; border-radius: 4px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px;
                text-align:right; } .terminal {color:#00DD00; font:14px verdana,sans-serif; background-color:#000000; border-radius: 6px;
                padding-left:10px; padding-right:10px; padding-bottom:4px; padding-top:2px; text-align:left; }
                #label {border: solid #CCC 1.0pt;
                text-align: right; font-family: Verdana; font-size: 10px; color: #333; font-weight: bold; vertical-align: middle;
                height: 20px; width:100px  } </style> </head>'''
    td_caixa = '<tr><td id="label">'
    td_data_mono = '<td style="font-family: Menlo, Consolas, Monaco, monospace;">'
    td_end = '</td></tr>\n'
    toto += '<pre>'
    # toto += '<b>         Tipo:</b> ' + ass_dict['proc_type'] + '<br>'
    # toto += '<b>       Numero:</b> #' + str(ass_dict['proc_id']) + '<br>'
    toto += '<b>      Unidade:</b> ' + ass_dict['proc_unit_name'] + '<br>'
    toto += '<b>         Data:</b> ' + ass_dict['proc_date'].strftime("%d-%m-%Y %H:%M") + '<br>'
    toto += '<b>       N.I.F.:</b> ' + ass_dict['cl_nif'] + '<br>'
    toto += '<b>       Morada:</b> ' + ass_dict['un_morada'] + ', ' + ass_dict['un_localidade'] + '<br>'
    # toto += '<b>      C.P.:</b>' + td_data + ass_dict['un_cp'] + '<br>'
    # toto += '</pre>'
    # toto += ''' <table>'''
    # if not ass_dict['proc_model'] == '':
    #     toto += td_caixa + 'Modelo:' + td_data + ass_dict['proc_model']
    # if not ass_dict['proc_serial_number'] == '':
    #     toto += '<td id="label">' + 'Num. de Série:' + td_data + ass_dict['proc_serial_number'] + td_end
    # toto += td_caixa + 'Problema:' + td_data + ass_dict['proc_reported'] + td_end
    toto += '-' * 80 + '<br>'
    toto += td_data_mono + ass_dict['proc_report_internal'].replace('\n', '<br>') + td_end
    toto += '-' * 80
    # toto += td_caixa + 'Meio:</h3>' + td_data + ass_dict['proc_meio'] + td_end
    # if not ass_dict['proc_quem'] == '':
    #     toto += td_caixa + 'Contacto:</h3>' + td_data + ass_dict['proc_quem'] + ' ' + ass_dict['proc_contacto'] + td_end
    # if not ass_dict['proc_report_invoice'] == '':
    #     toto += td_caixa + 'Relatório p/ Fac.:\n' + td_data + ass_dict['proc_report_invoice']
    # toto += td_caixa + 'Duração:</td>' + td_data + ass_dict['proc_duracao'].strftime("%H:%M") + td_end
    # toto += td_caixa + 'Técnico:</h3>' + td_data + ass_dict['proc_tecnico'] + td_end
    # toto += td_caixa + 'Estado:</h3>' + td_data + ass_dict['proc_status'] + td_end
    # toto += ''' </table>'''
    toto += '''<pre>'''
    toto += '<b> Proprietário:</b>' + ass_dict['cl_nome'] + '<br>'
    toto += '<b>       N.I.F.:</b>' + ass_dict['cl_nif'] + '<br>'
    toto += '<b>       Morada:</b>' + ass_dict['cl_morada'] + '<br>'
    toto += '<b>    Sede C.P.:</b>' + ass_dict['cl_cp'] + '<br>'
    if ass_dict['cl_cc'] > 0:
        toto += '<b>  C. Corrente: <font color="red" >' + '{0:.2f}'.format(ass_dict['cl_cc']) + '</b></font><br>'
    else:
        toto += '<b>  C. Corrente:</b>' + '{0:.2f}'.format(ass_dict['cl_cc']) + '<br>'
    
    toto += '<b>     Recebido:</b>' + ass_dict['proc_user'] + '<br>'
    toto += '</html>'
    # print(toto, file=open("output.html", "a"))
    return toto


def main():
    smtpmail.send_process_mail(20471)
    
    
if __name__ == '__main__':
    gl.conn_string = 'host=192.168.0.250 dbname=prism user=root password=masterkey'
    main()
