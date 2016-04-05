#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import os
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *
from connection import *
from baja import *

path = os.path.dirname(os.path.abspath(__file__))
ModificarDlgUI, ModificarDlgBase = uic.loadUiType(os.path.join(path, 'modificar.ui'))

class ModificarDialog(ModificarDlgBase, ModificarDlgUI):
    def __init__(self, parent = None):
        ModificarDlgBase.__init__(self, parent)
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
        ##Asignacion de eventos
        self.buttonBox.accepted.connect(self.buttonBox_OK)
        self.bajas_view.clicked.connect(self.bajas_clicked)
        ####

    def buttonBox_OK(self):
        self.baja.modificaSustituciones(self.inicio_dedit.date(),
                                        self.final_dedit.date())
        self.accept()

    def bajas_clicked(self, index):
        baja_id = index.sibling(index.row(),
                                self.model.fieldIndex("baja_id"))
        self.baja = Baja(baja_id.data())
        self.inicio_dedit.setEnabled(True)
        self.final_dedit.setEnabled(True)
        self.buttonBox.setEnabled(True)
        self.inicio_dedit.setDate(self.baja.inicio)    
        self.final_dedit.setDate(self.baja.final)
            
#######################################################################################
if __name__ == '__main__':
    app = QApplication([])
    if not createConnection():
        sys.exit(1)
    dlg = ModificarDialog()
    dlg.show()
    app.exec_()
##    if dlg.exec_():
##        print(dlg.getData())
