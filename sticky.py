#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout, QPlainTextEdit, QHBoxLayout, QPushButton


class StickyNote(QDialog):
    def __init__(self, text, parent=None):
        self.ret = False, ''
        super(StickyNote, self).__init__(parent)
        self.resize(600, 400)
        self.setWindowTitle('Relatório interno/comentários')
        masterLayout = QVBoxLayout(self)
        buttonLayout = QHBoxLayout()
        self.stickyNoteTxt = QPlainTextEdit()
        self.stickyNoteTxt.setStyleSheet("background-color: #ffffcc;")
        masterLayout.addWidget(self.stickyNoteTxt)
        ok = QPushButton('Valida')
        buttonLayout.addWidget(ok)
        ok.clicked.connect(self.ok_click)
        
        cancel = QPushButton('Cancela')
        cancel.clicked.connect(self.cancel_click)
        
        buttonLayout.addWidget(cancel)
        masterLayout.addLayout(buttonLayout)
        self.stickyNoteTxt.setPlainText(text)
    
    def ok_click(self):
        self.ret = True, self.stickyNoteTxt.toPlainText()
        self.close()
        
    def cancel_click(self):
        self.close()


def main():
    app = QApplication(sys.argv)
    form = StickyNote('')
    form.show()
    app.exec_()
    print(form.ret)


if __name__ == '__main__':
    main()
