#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtSql

import baja

from anadir_ui import Ui_Dialog

class AnadirDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)

        self.inicio_dedit.setDate(QtCore.QDate.currentDate())
        self.final_dedit.setDate(QtCore.QDate.currentDate())
        self.filtro_cbox.addItems(['Siglas', 'Nombre', 'Apellido1',
                                   'Apellido2', 'Equipo', 'Puesto'])
        self.motivo_cbox.addItems(['Baja medica', 'Formacion', 'Combustible',
                                   'Otros'])

        ##Configuracion del origen de datos
        self.model = QtSql.QSqlTableModel(self)
        self.model.setTable("personal")
        self.model.select()
        self.resultado_view.setModel(self.model)
        self.resultado_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.sel_model = self.resultado_view.selectionModel()
        self.encabezado = self.resultado_view.horizontalHeader()
        ####
        ####Configuracion visual de la tabla
        self.resultado_view.hideColumn(self.model.fieldIndex("personal_id"))
        self.resultado_view.hideColumn(self.model.fieldIndex("unidad"))
        self.model.setHeaderData(self.model.fieldIndex("siglas"),
                                 QtCore.Qt.Horizontal, "Siglas")
        self.model.setHeaderData(self.model.fieldIndex("nombre"),
                                 QtCore.Qt.Horizontal, "Nombre")
        self.model.setHeaderData(self.model.fieldIndex("apellido1"),
                                 QtCore.Qt.Horizontal, "Primer Apellido")
        self.model.setHeaderData(self.model.fieldIndex("apellido2"),
                                 QtCore.Qt.Horizontal, "Segundo Apellido")
        self.model.setHeaderData(self.model.fieldIndex("puesto"),
                                 QtCore.Qt.Horizontal, "Puesto")
        self.model.setHeaderData(self.model.fieldIndex("equipo"),
                                 QtCore.Qt.Horizontal, "Equipo")
        self.resultado_view.resizeColumnsToContents()
        ####
        ##Inhabilito OK en buttonbox
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        ####
        ##Asignacion de eventos
        self.sel_model.selectionChanged.connect(self.seleccionCambiada)
        self.buscar_ledit.textEdited.connect(self.buscar_text_edited)
        self.buttonBox.accepted.connect(self.buttonBox_OK)
        self.encabezado.sectionClicked.connect(self.encabezado_clicked)
        ####

    def buscar_text_edited(self):
        filtro = "{0} LIKE '{1}%'".format(self.filtro_cbox.currentText().lower(),
                                          self.buscar_ledit.text())
        self.model.setFilter(filtro)

    def buttonBox_OK(self):
        if self.inicio_dedit.date() > self.final_dedit.date():
            QtWidgets.QMessageBox.warning(self,
                                          "Error",
                                          "La fecha de inicio es "
                                          "posterior a la de fin")
            return False
        else:
            baja.Baja(self.trabajador_id.data(),
                      self.inicio_dedit.date(),
                      self.final_dedit.date(),
                      self.motivo_cbox.currentText())
            self.accept()

    def encabezado_clicked(self):
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

    def seleccionCambiada(self, selected, deselected):
        if selected.isEmpty():
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
            indices = selected.indexes()
            self.trabajador_id = indices[0].sibling(indices[0].row(),
                                                    self.model.fieldIndex("personal_id"))
            
#######################################################################################
if __name__ == '__main__':
    from connection import *
    app = QtWidgets.QApplication([])
    if not createConnection():
        sys.exit(1)
    dlg = AnadirDialog()
    dlg.show()
    app.exec_()
##    if dlg.exec_():
##        print(dlg.getData())
