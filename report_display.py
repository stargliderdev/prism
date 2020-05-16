# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QFileDialog
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5 import QtWebEngineWidgets
import qlib


class DisplayReport(QDialog):
    def __init__(self, html_report, size=(1024, 768), parent=None):
        super(DisplayReport, self).__init__(parent)
        mainLayout = QVBoxLayout(self)
        self.setWindowTitle('Relatório')
        self.resize(size[0], size[1])
        self.printBtn = QPushButton('Print')
        self.printBtn.clicked.connect(self.print_page)
        # self.printPreviewBtn = QPushButton('Preview')
        # self.printPreviewBtn.clicked.connect(self.filePrintPreview)
        self.printToPdfBtn = QPushButton('To PDF')
        self.printToPdfBtn.clicked.connect(self.print_to_pdf)
        self.exitBtn = QPushButton('Fechar')
        self.exitBtn.clicked.connect(self.exit_click)
        mainLayout.addLayout(
            qlib.addHLayout([self.printBtn, self.printToPdfBtn, True, self.exitBtn]))
        
        self.reportTextEdit = QtWebEngineWidgets.QWebEngineView(self)
        self.reportTextEdit.setHtml(html_report)
        self.printer = QPrinter()
        mainLayout.addWidget(self.reportTextEdit)
    
    def print_page(self):
        dlg = QPrintDialog(self.printer)
        if dlg.exec_():
            self.reportTextEdit.page().print(self.printer, self.print_completed)
    
    def print_completed(self, success):
        pass  # Do something in here, maybe update the status bar?
    
    def print_to_pdf(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Exporta para PDF", None, "PDF files (*.pdf);;All Files (*)")
        if fname:
            self.reportTextEdit.page().printToPdf(fname + '.pdf')
    
    def exit_click(self):
        self.close()


if __name__ == '__main__':
    pass
