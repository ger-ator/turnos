#!/usr/bin/python
# -*- coding: utf-8 -*-
 
from PyQt5 import QtCore, QtWidgets, QtSql

import trabajador

from asignar_ui import Ui_Dialog

class AsignarDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, sustitucion_id, parent = None):
        super().__init__(parent)
        self.setupUi(self)
        
        self.a_cubrir = trabajador.Sustitucion(sustitucion_id)

        ##METER UN CAMPO DE PRIORIDAD EN TABLA CANDIDATOS Y GESTIONAR DESDE LA CLASE
        ##POR EL MOMENTO ASI FUNCIONA
        query = QtSql.QSqlQuery()
        query.exec_("DELETE FROM candidatos")
        for i in self.a_cubrir.getListaCandidatos():
            query.prepare("INSERT INTO candidatos (sustituto_id, turno) "
                          "VALUES (?, ?)")
            query.addBindValue(i.getId())
            query.addBindValue(i.getTurno(self.a_cubrir.getFecha()).value)
            query.exec_()
        ####
        ##Configuro origen de datos
        self.model = QtSql.QSqlQueryModel(self)        
        self.populate_model()
        self.proxy_model = QtCore.QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.sustitutos_view.setModel(self.proxy_model)   
        ####
        ##Configuracion visual de la tabla
        self.sustitutos_view.hideColumn(0) ##sustituto_id
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Nombre")
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, "Primer Apellido")
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, "Segundo Apellido")
        self.model.setHeaderData(4, QtCore.Qt.Horizontal, "Puesto")
        self.model.setHeaderData(5, QtCore.Qt.Horizontal, "Unidad")
        self.model.setHeaderData(6, QtCore.Qt.Horizontal, "Turno")
        self.sustitutos_view.resizeColumnsToContents()
        ##Inhabilito OK en buttonbox
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        ####
        ##Asignacion de eventos
        self.buttonBox.accepted.connect(self.buttonBox_OK)
        self.sustitutos_view.doubleClicked.connect(self.sustitutos_dclicked)
        self.sustitutos_view.clicked.connect(self.sustitutos_clicked)
        ####

    def populate_model(self):
        self.model.setQuery("SELECT candidatos.sustituto_id, personal.nombre, "
                            "personal.apellido1, personal.apellido2, personal.puesto, "
                            "personal.unidad, candidatos.turno "
                            "FROM candidatos, personal "
                            "WHERE candidatos.sustituto_id = personal.personal_id ")
        self.sustitutos_view.resizeColumnsToContents()

    def buttonBox_OK(self):
        self.a_cubrir.asignaCandidato(self.trabajador_id.data())
        self.accept()

    def sustitutos_clicked(self, index):
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
        self.trabajador_id = index.sibling(index.row(), 0)##sustituto_id
            
    def sustitutos_dclicked(self, index):
        self.trabajador_id = index.sibling(index.row(), 0)##sustituto_id
        self.a_cubrir.asignaCandidato(trabajador_id.data())
        self.accept()
            
#######################################################################################
if __name__ == '__main__':
    import connection
    app = QtWidgets.QApplication([])
    if not connection.createConnection():
        import sys
        sys.exit(1)
    dlg = AsignarDialog(104)
    dlg.show()
    app.exec_()
##    if dlg.exec_():
##        print(dlg.getData())
