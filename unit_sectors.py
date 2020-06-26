#!/usr/bin/env python
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
import libpg


def simple_table():
    pdfmetrics.registerFont(TTFont('calibri', "calibri.ttf"))
    pdfmetrics.registerFont(TTFont('calibrib', "calibrib.ttf"))
    # and
    # unaccent(lower(authors.au_name))
    # LIKE
    # unaccent('%varios%')
    data = libpg.query_many('''select un_name, us_value1
       from unit_settings, unidades
            where us_unit_id= un_id and us_act_id = 16 and unidades.un_activa=True ''')
    # '%charlier,giraud%'
    doc = SimpleDocTemplate("simple_table.pdf", pagesize=A4, rightMargin=72,
                            leftMargin=62,
                            topMargin=30,
                            bottomMargin=18)
    styles = getSampleStyleSheet()
    story = []
    text = "<font face=calibri size=8>cabeçalho</font>"
    para = Paragraph(text, style=styles["Normal"])
    story.append(para)
    cnt = 1
    page_count = 1
    PAGE_BREAK = 75
    back_color = colors.lightgrey
    for n in data:
        # a = [n]
        # print(a)
        if cnt & 1:
            back_color = colors.lightgrey
        else:
            back_color = colors.white
        tblstyle = TableStyle([('ROWBACKGROUNDS', (0, 0), (-1, -1), [back_color, colors.green]),
                               ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                               ('FONT', (0, 0), (-1, -1), 'calibri', 8),
                               ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                               ('ALIGN', (1, 0), (1, -1), 'RIGHT')])
        
        tbl = Table([n], colWidths=[260, 30], rowHeights=[10 for x in range(len([n]))])
        if PAGE_BREAK == cnt:
            story.append(tbl)
            tbl.setStyle(tblstyle)
            para = Paragraph("<font face=calibri size=8>Página " + str(page_count) + "</font>", style=styles["Normal"])
            story.append(para)
            text = "<font face=calibri size=8>Livros" + "</font>"
            cnt = 1
            para = Paragraph(text, style=styles["Normal"])
            story.append(para)
            page_count += 1
        else:
            story.append(tbl)
            tbl.setStyle(tblstyle)
            cnt += 1
    story.append(para)
    doc.build(story)


if __name__ == '__main__':

    simple_table()