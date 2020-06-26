#!/usr/bin/python
# -*- coding: utf-8 -*-

CSS = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8">
        <style> body { background-color: #ffffff; font-size: 11x; font-family: Verdana; padding: 0; margin: 0;
        height: 100%; } tr.cores { background-color: #FFFFFF; } tr.cores:hover {
        background-color: #F8FBBD; } #linha_encP { border-bottom: solid #CCC 1.0pt; font-family: Verdana;
        font-size: 11px; color: #333333; height: 18px; } #linha2 { border-bottom: solid #0066CC 1.5pt;
        border-top: solid #0066CC 1.5pt; font-family: Verdana; font-size: 15px; color: #000080; height: 15px;
        background-color: #EAF1F7; } .cabecalho { border-top: solid #000 2.0pt; border-bottom: solid #000 1.0pt;
        font-weight: bold; font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 11px;
        background-color: #F8F8F8; } #caixa { border: solid #CCC 1.0pt; text-align: center; font-family: Verdana;
        font-size: 10px; color: #333; font-weight: bold; vertical-align: middle; height: 20px; } </style> '''

CSS_MONO = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8">
        <style> body { background-color: #ffffff; font-size: 11x; font-family: monospace; padding: 0; margin: 0;
        height: 100%; } tr.cores { background-color: #FFFFFF; } tr.cores:hover {
        background-color: #F8FBBD; } #linha_encP { border-bottom: solid #CCC 1.0pt; font-family: monospace;
        font-size: 13px; color: #333333; height: 18px; } #linha2 { border-bottom: solid #0066CC 1.5pt;
        border-top: solid #0066CC 1.5pt; font-family: monospace; font-size: 15px; color: #000080; height: 15px;
        background-color: #EAF1F7; } .cabecalho { border-top: solid #000 2.0pt; border-bottom: solid #000 1.0pt;
        font-weight: bold; font-family: monospace, Arial, Helvetica, sans-serif; font-size: 13px;
        background-color: #F8F8F8; } #caixa { border: solid #CCC 1.0pt; text-align: center; font-family: monospace;
        font-size: 10px; color: #333; font-weight: bold; vertical-align: middle; height: 20px; } </style> '''


def hardware_ages_report(hl):
    html = CSS
    html += '''
        <table width="900" align="center">
        <th id="cabecalho" width="200">Marca</th>
        <th id="cabecalho" width="200">Modelo</th>
        <th id="cabecalho" width="300">S/N</th>
        <th id="cabecalho" width="200">Idade</th>
        <th id="cabecalho" width="200">Estado</th>
        <th id="cabecalho" width="200">Tipo</th>
        '''
    if len(hl) > 0:
        for n in hl:
            html += '''<tr class="cores">'''
            html += '''<td id="linha_encP" align="left">''' + n[1] + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + n[2] + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + n[3] + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + n[4] + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + n[5] + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + n[6] + '</td>\n'
            html += '</tr>\n'
        html += '</table>'
    return html


def hardware_inventory_report(hl, unit_data):
    html = CSS_MONO
    html += '''<br><br>''' + 'Unidade:' + unit_data['un_name'].upper() + ''''''
    html += '''<hr>'''
    html += '''
        <table width="900" align="center">
        <th id="cabecalho" width="20"></th>
        <th id="cabecalho" width="200">Tipo</th>
        <th id="cabecalho" width="150">Marca</th>
        <th id="cabecalho" width="200">Modelo</th>
        <th id="cabecalho" width="250">S/N</th>
        '''
    if len(hl) > 0:
        for n in hl:
            html += '''<tr class="cores">'''
            html += '''<td id="linha_encP" align="left">''' + n[1] + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + n[2] + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + n[3] + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + n[4] + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + n[5] + '</td>\n'
            html += '</tr>\n'
        html += '</table>'
    else:
        html += '''</table>'''
    html += '<hr>'
    return html


def unit_grid_report(hl, headers):
    html = CSS
    html += ''' <table width="900" align="center">'''
    html += '''<th id="cabecalho" width="200">''' + headers[0] + '</th>'
    html += '''<th id="cabecalho" width="200">''' + headers[1] + '</th>'
    html += '''<th id="cabecalho" width="300">''' + headers[2] + '</th>'
    html += '''<th id="cabecalho" width="200">''' + headers[3] + '</th>'
    html += '''<th id="cabecalho" width="200">''' + headers[4] + '</th>'
    
    if len(hl) > 0:
        for n in hl:
            html += '''<tr class="cores">'''
            html += '''<td id="linha_encP" align="left">''' + n[0] + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + n[1] + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + n[2] + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + n[3] + '</td>\n'
            html += '''<td id="linha_encP" align="left">''' + n[4] + '</td>\n'
            html += '</tr>\n'
        html += '</table>'
    return html

