#!/usr/bin/python
# -*- coding: utf-8 -*-
 
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *
from connection import *
from trabajador import *
from asignar_ui import Ui_Dialog

class AsignarDialog(QDialog, Ui_Dialog):
    def __init__(self, sustitucion_id, parent = None):
        super().__init__(parent)
        self.setupUi(self)
        
        self.a_cubrir = Sustitucion(sustitucion_id)

        ##METER UN CAMPO DE PRIORIDAD EN TABLA CANDIDATOS Y GESTIONAR DESDE LA CLASE
        ##POR EL MOMENTO ASI FUNCIONA
        query = QSqlQuery()
        query.exec_("DELETE FROM candidatos")
        for i in self.a_cubrir.getListaCandidatos():
            query.prepare("INSERT INTO candidatos (sustituto_id, turno) "
                          "VALUES (?, ?)")
            query.addBindValue(i.getId())
            query.addBindValue(i.getTurno(self.a_cubrir.getFecha()).value)
            query.exec_()
        ####

        ##Configuro origen de datos
        self.model = QSqlRelationalTableModel()
        self.model.setTable("candidatos")
        self.model.setRelation(self.model.fieldIndex("sustituto_id"),
                               QSqlRelation("personal",
                                            "personal_id",
                                            "personal_id, nombre, apellido1, apellido2, puesto, unidad"))
        self.model.select()
        self.sustitutos_view.setModel(self.model)
        self.sustitutos_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        ####
        ##Configuracion visual de la tabla
        self.sustitutos_view.hideColumn(self.model.fieldIndex("candidatos_id"))
        self.sustitutos_view.hideColumn(self.model.fieldIndex("personal_id"))
        self.model.setHeaderData(self.model.fieldIndex("nombre"),
                                 Qt.Horizontal, "Nombre")
        self.model.setHeaderData(self.model.fieldIndex("apellido1"),
                                 Qt.Horizontal, "Primer Apellido")
        self.model.setHeaderData(self.model.fieldIndex("apellido2"),
                                 Qt.Horizontal, "Segundo Apellido")
        self.model.setHeaderData(self.model.fieldIndex("puesto"),
                                 Qt.Horizontal, "Puesto")
        self.model.setHeaderData(self.model.fieldIndex("unidad"),
                                 Qt.Horizontal, "Unidad")
        self.model.setHeaderData(self.model.fieldIndex("turno"),
                                 Qt.Horizontal, "Turno")
        self.sustitutos_view.resizeColumnsToContents()
        ##Inhabilito OK en buttonbox
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        ####
        ##Asignacion de eventos
        self.buttonBox.accepted.connect(self.buttonBox_OK)
        self.sustitutos_view.doubleClicked.connect(self.sustitutos_dclicked)
        self.sustitutos_view.clicked.connect(self.sustitutos_clicked)
        ####

    def buttonBox_OK(self):
        self.a_cubrir.asignaCandidato(self.trabajador_id.data())
        self.accept()

    def sustitutos_clicked(self, index):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        self.trabajador_id = index.sibling(index.row(),
                                           self.model.fieldIndex("personal_id"))
            
    def sustitutos_dclicked(self, index):
        self.trabajador_id = index.sibling(index.row(),
                                      self.model.fieldIndex("personal_id"))
        self.a_cubrir.asignaCandidato(trabajador_id.data())
        self.accept()
            
#######################################################################################
if __name__ == '__main__':
    app = QApplication([])
    if not createConnection():
        sys.exit(1)
    dlg = AsignarDialog(81)
    dlg.show()
    app.exec_()
##    if dlg.exec_():
##        print(dlg.getData())
