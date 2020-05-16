#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QTableWidget, QPushButton, QHBoxLayout,QApplication, QToolButton,  QMessageBox
import sys
import ex_grid
import libpg
import qlib as qc
import models_lib


class ModelsBrowser(QDialog):
    def __init__(self, conf, parent=None):
        super(ModelsBrowser, self).__init__(parent)
        self.resize(1024, 600)
        self.setWindowTitle('Modelos')
        # self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
        masterLayout = QVBoxLayout(self)
        self.settings = conf
        self.tag_list = ''
        self.toto = ()
        self.ret = {}
        self.searchEdit = QLineEdit()
        self.searchEdit.setMaximumWidth(200)
        self.searchEdit.textChanged.connect(self.brand_search_changed)
        closeBtn = QPushButton()
        closeBtn.setText('Sair')
        closeBtn.setFocusPolicy(0)  # Qt.NoFocus
        closeBtn.clicked.connect(self.exit_click)
        masterLayout.addLayout(qc.addHLayout([self.searchEdit, True, closeBtn]))
        gridContainLayout = QHBoxLayout()
        self.brandsGrid = QTableWidget()
        self.brandsGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.brandsGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.brandsGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.brandsGrid.verticalHeader().setDefaultSectionSize(20)
        self.brandsGrid.verticalHeader().setVisible(False)
        self.brandsGrid.resizeColumnsToContents()
        self.brandsGrid.setMaximumWidth(200)
        self.brandsGrid.setAlternatingRowColors(True)
        self.brandsGrid.setStyleSheet("alternate-background-color: #e6f2ff;")
        self.brandsGrid.itemDoubleClicked.connect(self.models_refresh)
        addBrand = QToolButton()
        addBrand.setText('+')
        addBrand.clicked.connect(self.brands_add_click)
        removeBrand = QToolButton()
        removeBrand.setText('-')
        removeBrand.clicked.connect(self.brand_deactivate_click)
        dum1Layout = QVBoxLayout()
        dum1Layout.addWidget(self.brandsGrid)
        dum1Layout.addLayout(qc.addHLayout([addBrand,removeBrand]))
        gridContainLayout.addLayout(dum1Layout)
        
        self.modelsGrid = QTableWidget()
        self.modelsGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.modelsGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.modelsGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.modelsGrid.verticalHeader().setDefaultSectionSize(20)
        self.modelsGrid.verticalHeader().setVisible(False)
        self.modelsGrid.resizeColumnsToContents()
        self.modelsGrid.setAlternatingRowColors(True)
        self.modelsGrid.setStyleSheet("alternate-background-color: #e6fff2;")
        self.modelsGrid.itemDoubleClicked.connect(self.model_edit_click)
        addModel = QToolButton()
        addModel.setText('+')
        addModel.clicked.connect(self.model_add_click)
        removeModel = QToolButton()
        removeModel.setText('-')
        removeModel.clicked.connect(self.model_deactivate_click)
        dum2Layout = QVBoxLayout()
        dum2Layout.addWidget(self.modelsGrid)
        dum2Layout.addLayout(qc.addHLayout([addModel, removeModel, True]))
        gridContainLayout.addLayout(dum2Layout)
        masterLayout.addLayout(gridContainLayout)
        exit_btn = QPushButton('Sair')
        exit_btn.clicked.connect(self.exit_click)
        self.brands_refresh()
    
    def models_refresh(self):
        b = int(self.brandsGrid.item(self.brandsGrid.currentRow(), 0).text())
        sql = '''select md_id, md_name,hw_type_name,  (select count (hw_id) from hardware where hw_model_id=md_id and hw_status_id in(0,1)) as stk_act,
       (select count (hw_id) from hardware where hw_model_id=md_id and hw_status_id=2) as down,md_ref_gc
                 from models, hardware_types
                 where md_brand_id= %s and hw_type_id=md_hardware_type
                 order by md_name'''
        dataset = libpg.query_many(sql, (b,))
        ex_grid.ex_grid_update(self.modelsGrid, {0: ['ID', 'i'], 1: ['Modelo', 's'], 2: ['Tipo', 's'], 3: ['Act', 'i'],4: ['Des', 'i'],5: ['Ref OEM', 's']}, dataset, hidden=0)
        self.modelsGrid.setColumnWidth(0, 80)
        self.modelsGrid.setColumnWidth(1, 200)
        self.modelsGrid.setColumnWidth(2, 150)
        self.modelsGrid.setColumnWidth(3, 40)
        self.modelsGrid.setColumnWidth(4, 40)
        self.modelsGrid.setColumnWidth(5, 250)

    def model_edit_click(self):
        if self.settings['mode'] == 0:
            model = int(self.modelsGrid.item(self.modelsGrid.currentRow(), 0).text())
            brand_id = int(self.brandsGrid.item(self.brandsGrid.currentRow(), 0).text())
            brand_name = self.brandsGrid.item(self.brandsGrid.currentRow(), 1).text()
            form = models_lib.ModelEdit(model, brand_id, brand_name)
            form.exec()
            self.models_refresh()
        else:
            model = int(self.modelsGrid.item(self.modelsGrid.currentRow(), 0).text())
            model_txt = self.modelsGrid.item(self.modelsGrid.currentRow(), 1).text()
            brand_id = int(self.brandsGrid.item(self.brandsGrid.currentRow(), 0).text())
            brand_name = self.brandsGrid.item(self.brandsGrid.currentRow(), 1).text()
            hardware_type = self.modelsGrid.item(self.modelsGrid.currentRow(), 2).text()
            self.ret = {'model_id': model, 'brand_id': brand_id,'brand_name': brand_name, 'model_name': model_txt, 'hw_type_name': hardware_type}
            self.close()
    
    def model_add_click(self):
        try:
            brand_id = int(self.brandsGrid.item(self.brandsGrid.currentRow(), 0).text())
            brand_name = self.brandsGrid.item(self.brandsGrid.currentRow(), 1).text()
            form = models_lib.ModelEdit(-1, brand_id, brand_name)
            form.exec_()
            self.models_refresh()
        except AttributeError:
            QMessageBox.warning(None, "Erro", "Escolher a Marca!")

    def model_deactivate_click(self):
        try:
            model = int(self.modelsGrid.item(self.modelsGrid.currentRow(), 0).text())
            model_qtd = int(self.modelsGrid.item(self.modelsGrid.currentRow(), 3).text()) + int(self.modelsGrid.item(self.modelsGrid.currentRow(), 3).text())
            if model_qtd >0:
                pass
            else:
                sql = 'delete from models where md_id=%s'
                libpg.execute_query(sql, (model,))
                self.models_refresh()
        except AttributeError:
            pass
        
    def brands_refresh(self):
        sql = '''select br_id,br_name from brands where br_active = True order by br_name '''
        dataset = libpg.query_many(sql, True)
        ex_grid.ex_grid_update(self.brandsGrid, {0: ['ID', 'i'], 1: ['Marca', 's']}, dataset, hidden=0)
        # self.brandsGrid.horizontalHeader().setVisible(False)
        self.brandsGrid.setColumnWidth(0, 80)
        self.brandsGrid.setColumnWidth(1, 200)
    
    def brand_search_changed(self, text):
        search = '\'' + str(text).lower() + '%%\''
        sql = '''select br_id, br_name from brands where lower(br_name) like ''' + search + ''' order by br_name'''
        dataset = libpg.query_many(sql, True)
        ex_grid.ex_grid_update(self.brandsGrid, {0: ['ID', 'i'], 1: ['Nome', 's']}, dataset, hidden=0)
        self.modelsGrid.setRowCount(0)
        
    def brands_add_click(self):
        form = models_lib.AddBrand()
        form.exec_()
        self.brands_refresh()
    
    def brand_deactivate_click(self):
        pass
    
    def exit_click(self):
        self.close()


def main():
    app = QApplication(sys.argv)
    cf = {'mode': 0}
    form = ModelsBrowser(cf)
    form.show()
    app.exec_()
    print(form.ret)


if __name__ == '__main__':
    main()