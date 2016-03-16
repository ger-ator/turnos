#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import os
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *
from connection import *
import datetime

path = os.path.dirname(os.path.abspath(__file__))
AnadirDlgUI, AnadirDlgBase = uic.loadUiType(os.path.join(path, 'anadir.ui'))

class AnadirDialog(AnadirDlgBase, AnadirDlgUI):
    def __init__(self, parent = None):
        AnadirDlgBase.__init__(self, parent)
        self.setupUi(self)

        self.inicio_dedit.setDate(QDate.currentDate())
        self.final_dedit.setDate(QDate.currentDate())
        self.filtro_cbox.addItems(['Siglas', 'Nombre', 'Apellido1',
                                   'Apellido2', 'Equipo', 'Puesto'])

        self.model = QSqlQueryModel(self)
        self.model.setQuery("SELECT Id, Siglas, Nombre, Apellido1, Apellido2, Puesto, Equipo "
                            "FROM personal")
        self.resultado_view.setModel(self.model)
        self.resultado_view.hideColumn(0) ##Id
        self.resultado_view.resizeColumnsToContents()

        self.buscar_ledit.textEdited.connect(self.buscar_text_edited)
        self.buttonBox.accepted.connect(self.buttonBox_OK)

    def buscar_text_edited(self):
        query = QSqlQuery()
        query.prepare("SELECT Id, Siglas, Nombre, Apellido1, Apellido2, Puesto, Equipo "
                      "from personal WHERE {0} = ?".format(self.filtro_cbox.currentText()))        
        query.addBindValue(self.buscar_ledit.text())
        query.exec_()
        self.model.setQuery(query)

    def buttonBox_OK(self):
        fila = self.resultado_view.selectedIndexes()
        
        if fila == []:
            QMessageBox.warning(self, "Error", "No has seleccionado ningun trabajador")
            return False
        elif self.inicio_dedit.date() > self.final_dedit.date():
            QMessageBox.warning(self, "Error", "La fecha de inicio es posterior a la de fin")
            return False
        else:
            trabajador_id = fila[0].sibling(fila[0].row(), 0)
            insertBaja(trabajador_id.data(),
                       self.inicio_dedit.date(),
                       self.final_dedit.date())
            self.accept()
            
#######################################################################################
if __name__ == '__main__':
    app = QApplication([])
    if not createConnection():
        sys.exit(1)
    dlg = AnadirDialog()
    dlg.show()
    app.exec_()
##    if dlg.exec_():
##        print(dlg.getData())
