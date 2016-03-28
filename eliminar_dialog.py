#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import os
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *
from connection import *

path = os.path.dirname(os.path.abspath(__file__))
EliminarDlgUI, EliminarDlgBase = uic.loadUiType(os.path.join(path, 'eliminar.ui'))

class EliminarDialog(EliminarDlgBase, EliminarDlgUI):
    def __init__(self, parent = None):
        EliminarDlgBase.__init__(self, parent)
        self.setupUi(self)

        self.model = QSqlQueryModel(self)

        self.model.setQuery("SELECT bajas.baja_id, personal.nombre, personal.apellido1, "
                            "personal.apellido2, bajas.inicio, bajas.final "
                            "FROM bajas "
                            "LEFT JOIN personal ON bajas.sustituido_id = personal.personal_id")

        self.bajas_view.setModel(self.model)

        self.bajas_view.hideColumn(0) ##Id

        self.bajas_view.resizeColumnsToContents()

        self.buttonBox.accepted.connect(self.buttonBox_OK)
        self.bajas_view.doubleClicked.connect(self.bajas_dclicked)

    def buttonBox_OK(self):
        fila = self.bajas_view.selectedIndexes()
     
        if fila == []:
            QMessageBox.warning(self, "Error", "No has seleccionado ninguna baja.")
            return False
        else:
            self.bajas_dclicked(fila[0])
            
    def bajas_dclicked(self, index):
        bajas_id = index.sibling(index.row(),0)
        query = QSqlQuery()
        query.prepare("DELETE FROM sustituciones WHERE baja_id = ?")
        query.addBindValue(bajas_id.data())
        query.exec_()
        query.prepare("DELETE FROM bajas WHERE baja_id = ?")
        query.addBindValue(bajas_id.data())
        query.exec_()
        self.accept()    
            
#######################################################################################
if __name__ == '__main__':
    app = QApplication([])
    if not createConnection():
        sys.exit(1)
    dlg = EliminarDialog()
    dlg.show()
    app.exec_()
##    if dlg.exec_():
##        print(dlg.getData())
