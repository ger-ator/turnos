#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import os
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *
from connection import *
from trabajador import *

path = os.path.dirname(os.path.abspath(__file__))
AsignarDlgUI, AsignarDlgBase = uic.loadUiType(os.path.join(path, 'asignar.ui'))

class AsignarDialog(AsignarDlgBase, AsignarDlgUI):
    def __init__(self, necesidad_id, parent = None):
        AsignarDlgBase.__init__(self, parent)
        self.setupUi(self)
        
        self.a_cubrir = Necesidad(necesidad_id)

        ##ÑAPA PARA ORDENAR POR LISTA
        ##SQLITE NO SOPORTA ORDER BY FIELD
        ##CREO UNA TABLA TEMPORAL E INSERTO EN ORDEN
        ##LUEGO HAGO UN ORDER BY Id
        ##YA LA APROVECHO PARA METER EL TURNO DEL CANDIDATO
        ##Y NO COMPICAR MAS LAS QUERYS
        query = QSqlQuery()
        query.exec_("DROP TABLE temporal")
        query.exec_("CREATE TABLE temporal ("
                    "Id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "Turno TEXT, "
                    "trabajadorid INTEGER)")
        for i in self.a_cubrir.getCandidatos():
            query.prepare("INSERT INTO temporal (trabajadorid, Turno) "
                          "VALUES (?, ?)")
            query.addBindValue(i.getId())
            query.addBindValue(i.getTurno(self.a_cubrir.getFecha()))
            query.exec_()

        querystr = ("SELECT personal.Id, personal.Nombre, "
                    "personal.Apellido1, personal.Apellido2, "
                    "personal.Puesto, personal.Unidad, temporal.Turno "
                    "FROM temporal "
                    "LEFT JOIN personal ON temporal.trabajadorid = personal.Id "
                    "ORDER BY temporal.Id ASC")
        self.model = QSqlQueryModel(self)
        self.model.setQuery(querystr)
        self.sustitutos_view.setModel(self.model)
        self.sustitutos_view.resizeColumnsToContents()
        self.sustitutos_view.hideColumn(0) ##Id

        self.buttonBox.accepted.connect(self.buttonBox_OK)
        self.sustitutos_view.doubleClicked.connect(self.sustitutos_dclicked)

    def buttonBox_OK(self):
        fila = self.sustitutos_view.selectedIndexes()
     
        if fila == []:
            QMessageBox.warning(self, "Error", "No has seleccionado ningun trabajador")
            return False
        else:
            self.sustitutos_dclicked(fila[0])
            
    def sustitutos_dclicked(self, index):
        trabajador_id = index.sibling(index.row(),0)
        self.a_cubrir.asignaCandidato(trabajador_id.data())
##        query = QSqlQuery()
##        query.prepare("UPDATE necesidades SET Asignado = ? WHERE Id = ?")
##        query.addBindValue(trabajador_id.data())
##        query.addBindValue(self.a_cubrir.getId())        
##        query.exec_()
        self.accept()        
            
#######################################################################################
if __name__ == '__main__':
    app = QApplication([])
    if not createConnection():
        sys.exit(1)
    dlg = AsignarDialog(23)
    dlg.show()
    app.exec_()
##    if dlg.exec_():
##        print(dlg.getData())
