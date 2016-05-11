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
        ##Por defecto buscar_cbox esta oculto
        self.buscar_cbox.hide()
        ####
        ##Asignacion de eventos
        self.sel_model.selectionChanged.connect(self.seleccionCambiada)
        self.filtro_cbox.currentIndexChanged.connect(self.filtro_sel_changed)
        self.buscar_cbox.currentIndexChanged.connect(self.filtro_cbox_edited)
        self.buscar_ledit.textEdited.connect(self.filtro_text_edited)
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

    def filtro_sel_changed(self, index):
        if index == 4:
            self.buscar_ledit.hide()
            self.buscar_cbox.clear()
            self.buscar_cbox.show()
            query = QtSql.QSqlQuery()
            query.exec_("SELECT puesto FROM puestos "
                        "ORDER BY puesto_id ASC")
            while query.next():
                self.buscar_cbox.addItem(query.value(0))            
        elif index == 5:
            self.buscar_ledit.hide()
            self.buscar_cbox.clear()
            self.buscar_cbox.show()
            query = QtSql.QSqlQuery()
            query.exec_("SELECT grupo FROM grupos "
                        "ORDER BY grupo_id ASC")
            while query.next():
                self.buscar_cbox.addItem(query.value(0))
        else:
            self.buscar_ledit.show()
            self.buscar_cbox.hide()
            self.proxy_model.setFilterRegExp("")
        self.proxy_model.setFilterKeyColumn(index)

    def filtro_text_edited(self, texto):
        filtro = QtCore.QRegExp("^{0}".format(texto),
                                QtCore.Qt.CaseInsensitive,
                                QtCore.QRegExp.RegExp)
        self.proxy_model.setFilterRegExp(filtro)

    def filtro_cbox_edited(self, index):
        filtro = QtCore.QRegExp("^{0}".format(self.buscar_cbox.currentText()),
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
            ##Inserta la baja
            trabajador_id = self.sel_model.selectedRows(6)#personal_id
            sustituido_id = trabajador_id[0].data()
            inicio = self.inicio_dedit.date()
            final = self.final_dedit.date()
            
            mis_bajas = bajas.Bajas()
            mis_bajas.add(sustituido_id, inicio, final,
                          self.motivo_cbox.currentText())
            ##Comprueba si el personal de baja esta sustituyendo a alguien
            ##y elimina la asignacion
            mis_sustituciones = bajas.Sustituciones()
            for sustitucion in mis_sustituciones.iterable():
                if sustitucion.sustituto() == sustituido_id:
                    if inicio <= sustitucion.fecha() <= final:
                        sustitucion.setSustituto(None)                    
            self.accept()

    def seleccionCambiada(self, selected, deselected):
        if selected.isEmpty():
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
        
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
