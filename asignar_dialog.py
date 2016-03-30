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
    def __init__(self, sustitucion_id, parent = None):
        AsignarDlgBase.__init__(self, parent)
        self.setupUi(self)
        
        self.a_cubrir = Sustitucion(sustitucion_id)

        ##ÑAPA PARA ORDENAR POR LISTA
        ##SQLITE NO SOPORTA ORDER BY FIELD
        ##CREO UNA TABLA TEMPORAL E INSERTO EN ORDEN
        ##LUEGO HAGO UN ORDER BY Id
        ##YA LA APROVECHO PARA METER EL TURNO DEL CANDIDATO
        ##Y NO COMPICAR MAS LAS QUERYS
        query = QSqlQuery()
        query.exec_("DROP TABLE temporal")
        query.exec_("CREATE TABLE temporal ("
                    "temporal_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "turno TEXT, "
                    "sustituto_id INTEGER)")
        for i in self.a_cubrir.getListaCandidatos():
            query.prepare("INSERT INTO temporal (sustituto_id, turno) "
                          "VALUES (?, ?)")
            query.addBindValue(i.getId())
            query.addBindValue(i.getTurno(self.a_cubrir.getFecha()).value)
            query.exec_()

        querystr = ("SELECT personal.personal_id, personal.nombre, "
                    "personal.apellido1, personal.apellido2, "
                    "personal.puesto, personal.unidad, temporal.turno "
                    "FROM temporal "
                    "LEFT JOIN personal ON temporal.sustituto_id = personal.personal_id "
                    "ORDER BY temporal.temporal_id ASC")
        self.model = QSqlQueryModel(self)
        self.model.setQuery(querystr)
        self.sustitutos_view.setModel(self.model)
        self.sustitutos_view.resizeColumnsToContents()
        self.sustitutos_view.hideColumn(0) ##Id
        
##        sustitutos_id = [str(i.getId()) for i in self.a_cubrir.getListaCandidatos()]
##            
##        
##        self.model = QSqlRelationalTableModel()
##        self.model.setTable("personal")
##        self.model.setFilter("personal_id IN ({0})".format(", ".join(sustitutos_id)))
##        self.model.setRelation(self.model.fieldIndex("baja_id"),
##                               QSqlRelation("personal",
##                                            "personal_id",
##                                            "nombre, apellido1, apellido2, puesto, unidad"))
##        self.model.setSort("CASE")
##        self.sustitutos_view.setModel(self.model)
##ORDER BY 
##  CASE turno
##    WHEN 'reten' THEN 0
##    WHEN 'oficina' THEN 1
##    WHEN 'descanso' THEN 2
##  END

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
        self.accept()        
            
#######################################################################################
if __name__ == '__main__':
    app = QApplication([])
    if not createConnection():
        sys.exit(1)
    dlg = AsignarDialog(1)
    dlg.show()
    app.exec_()
##    if dlg.exec_():
##        print(dlg.getData())
