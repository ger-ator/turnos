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

        ##Configuracion del origen de datos
        self.model = QSqlQueryModel(self)
        self.model = QSqlRelationalTableModel()
        self.model.setTable("bajas")
        self.model.setJoinMode(QSqlRelationalTableModel.InnerJoin)
        self.model.setRelation(self.model.fieldIndex("sustituido_id"),
                               QSqlRelation("personal",
                                            "personal_id",
                                            "nombre, apellido1, apellido2"))
        self.bajas_view.setModel(self.model)
        self.model.select()
        self.bajas_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        ####
        ##Configuracion visual de la tabla
        self.bajas_view.hideColumn(self.model.fieldIndex("baja_id"))
        self.model.setHeaderData(self.model.fieldIndex("nombre"),
                                 Qt.Horizontal, "Nombre")
        self.model.setHeaderData(self.model.fieldIndex("apellido1"),
                                 Qt.Horizontal, "Primer Apellido")
        self.model.setHeaderData(self.model.fieldIndex("apellido2"),
                                 Qt.Horizontal, "Segundo Apellido")
        self.model.setHeaderData(self.model.fieldIndex("inicio"),
                                 Qt.Horizontal, "Desde")
        self.model.setHeaderData(self.model.fieldIndex("final"),
                                 Qt.Horizontal, "Hasta")
        self.model.setHeaderData(self.model.fieldIndex("motivo"),
                                 Qt.Horizontal, "Motivo")
        self.bajas_view.resizeColumnsToContents()
        ####
        ##Inhabilito OK en buttonbox
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        ####
        ##Asignacion de eventos
        self.buttonBox.accepted.connect(self.buttonBox_OK)
        self.bajas_view.doubleClicked.connect(self.bajas_dclicked)
        self.bajas_view.clicked.connect(self.bajas_clicked)
        ####

    def buttonBox_OK(self):
        query = QSqlQuery()
        query.prepare("DELETE FROM sustituciones WHERE baja_id = ?")
        query.addBindValue(self.bajas_id.data())
        query.exec_()
        query.prepare("DELETE FROM bajas WHERE baja_id = ?")
        query.addBindValue(self.bajas_id.data())
        query.exec_()
        self.accept()

    def bajas_clicked(self, index):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        self.bajas_id = index.sibling(index.row(),
                                      self.model.fieldIndex("baja_id"))
            
    def bajas_dclicked(self, index):
        bajas_id = index.sibling(index.row(),
                                 self.model.fieldIndex("baja_id"))
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
