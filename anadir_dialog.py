#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtSql

from personal import bajas

from ui.anadir_ui import Ui_Dialog

class AnadirDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)

        self.inicio_dedit.setDate(QtCore.QDate.currentDate())
        self.final_dedit.setDate(QtCore.QDate.currentDate())
        self.filtro_cbox.addItems(['Siglas', 'Nombre', 'Primer Apellido',
                                   'Segundo Apellido', 'Puesto', 'Equipo'])
        self.motivo_cbox.addItems(['Baja medica', 'Formacion', 'Combustible',
                                   'Otros'])

        ##Configuracion del origen de datos
        self.model = QtSql.QSqlQueryModel(self)
        self.populate_model()
        self.proxy_model = QtCore.QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)    
        self.resultado_view.setModel(self.proxy_model)
        self.sel_model = self.resultado_view.selectionModel()
        ####
        ####Configuracion visual de la tabla
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, "Siglas")
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Nombre")
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, "Primer Apellido")
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, "Segundo Apellido")
        self.model.setHeaderData(4, QtCore.Qt.Horizontal, "Puesto")
        self.model.setHeaderData(5, QtCore.Qt.Horizontal, "Equipo")
        self.resultado_view.hideColumn(6) ##personal_id
        self.resultado_view.resizeColumnsToContents()
        ####
        ##Inhabilito OK en buttonbox
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        ####
        ##Asignacion de eventos
        self.sel_model.selectionChanged.connect(self.seleccionCambiada)
        self.buscar_ledit.textEdited.connect(self.filtro_text_edited)
        self.filtro_cbox.currentIndexChanged.connect(self.proxy_model.setFilterKeyColumn)
        self.buttonBox.accepted.connect(self.buttonBox_OK)
        ####

    def populate_model(self):
        self.model.setQuery("SELECT personal.siglas, personal.nombre, "
                            "personal.apellido1, personal.apellido2, "
                            "puestos.puesto, grupos.grupo, personal.personal_id "
                            "FROM personal "
                            "INNER JOIN grupos "
                            "ON grupos.grupo_id=personal.grupo "
                            "INNER JOIN puestos "
                            "ON puestos.puesto_id=personal.puesto ")
        self.resultado_view.resizeColumnsToContents()

    def filtro_text_edited(self, texto):
        filtro = QtCore.QRegExp("^{0}".format(texto),
                                QtCore.Qt.CaseInsensitive,
                                QtCore.QRegExp.RegExp)
        self.proxy_model.setFilterRegExp(filtro)

    def buttonBox_OK(self):
        if self.inicio_dedit.date() > self.final_dedit.date():
            QtWidgets.QMessageBox.warning(self,
                                          "Error",
                                          "La fecha de inicio es "
                                          "posterior a la de fin")
            return False
        else:
            mis_bajas = bajas.Bajas()
            mis_bajas.add(self.trabajador_id.data(),
                          self.inicio_dedit.date(),
                          self.final_dedit.date(),
                          self.motivo_cbox.currentText())
            self.accept()

    def seleccionCambiada(self, selected, deselected):
        if selected.isEmpty():
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
            indices = selected.indexes()
            self.trabajador_id = indices[0].sibling(indices[0].row(), 6)##personal_id
        
#######################################################################################
##if __name__ == '__main__':
##    import connection
##    app = QtWidgets.QApplication([])
##    if not connection.createConnection():
##        import sys
##        sys.exit(1)
##    dlg = AnadirDialog()
##    dlg.show()
##    app.exec_()
##    if dlg.exec_():
##        print(dlg.getData())
