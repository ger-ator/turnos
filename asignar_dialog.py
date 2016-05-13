#!/usr/bin/python
# -*- coding: utf-8 -*-
 
from PyQt5 import QtCore, QtWidgets, QtSql

from personal import bajas, trabajador, personal, calendario

from ui.asignar_ui import Ui_Dialog

class AsignarDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, sustitucion_id, parent = None):
        super().__init__(parent)
        self.setupUi(self)
        
        self.sustitucion = bajas.Sustitucion(None, sustitucion_id)
        self.inicio_dedit.setDate(QtCore.QDate.currentDate())
        self.final_dedit.setDate(QtCore.QDate.currentDate())
        ##Configuro origen de datos
        self.model = QtSql.QSqlQueryModel(self)
        self.populate_model()
        self.proxy_model = QtCore.QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.sustitutos_view.setModel(self.proxy_model)
        self.sel_model = self.sustitutos_view.selectionModel()
        ####
        ##Filtrar por IDs de posibles sustitutos
        filtro = "|".join(["^{0}$".format(personal.rowid())
                           for personal in self.sustitucion.sustitutos()])
        self.proxy_model.setFilterKeyColumn(0)##personal_id
        self.proxy_model.setFilterRegExp(filtro)
        ####
        ##Configuracion visual de la tabla
        self.sustitutos_view.hideColumn(0) ##sustituto_id
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Nombre")
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, "Primer Apellido")
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, "Segundo Apellido")
        self.model.setHeaderData(4, QtCore.Qt.Horizontal, "Puesto")
        self.model.setHeaderData(5, QtCore.Qt.Horizontal, "Unidad")
        self.model.setHeaderData(6, QtCore.Qt.Horizontal, "Turno")
        self.sustitutos_view.hideColumn(7) ##unidad para oder by
        self.sustitutos_view.hideColumn(8) ##jornada para oder by
        self.sustitutos_view.resizeColumnsToContents()
        ##Inhabilito OK en buttonbox
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        ####
        ##Configuracion del combobox de modo de asignacion
        self.modo_cbox.addItems(["Asignación simple",
                                 "Tratar de asignar en días seleccionados",
                                 "Asignar automáticamente la mejor opción"])
        ####
        ##Asignacion de eventos
        self.sel_model.selectionChanged.connect(self.seleccionCambiada)
        self.buttonBox.accepted.connect(self.buttonBox_OK)
        self.sustitutos_view.doubleClicked.connect(self.buttonBox_OK)
        self.modo_cbox.currentIndexChanged.connect(self.modo_changed)
        ####

    def populate_model(self):    
        query = QtSql.QSqlQuery()
        text_query = ("SELECT "
                      "personal.personal_id, personal.nombre, "
                      "personal.apellido1, personal.apellido2, "
                      "puestos.puesto, unidad.unidad, "
                      "jornadas.turno, personal.unidad, calendario.jornada "
                      "FROM personal "
                      "INNER JOIN calendario "
                      "ON calendario.grupo = personal.grupo "
                      "INNER JOIN jornadas "
                      "ON jornadas.turno_id=calendario.jornada "
                      "INNER JOIN puestos "
                      "ON puestos.puesto_id=personal.puesto "
                      "INNER JOIN unidad "
                      "ON unidad.unidad_id=personal.unidad "
                      "WHERE calendario.fecha = ? "
                      "ORDER BY calendario.jornada, personal.unidad ")
        if self.sustitucion.sustituido().unidad() is personal.Unidad.U2:
            text_query = text_query + "DESC"            
        query.prepare(text_query)
        query.addBindValue(self.sustitucion.fecha())            
        if not query.exec_():
            print(query.lastError().text())            
        self.model.setQuery(query)
        self.sustitutos_view.resizeColumnsToContents()

    def modo_changed(self, index):
        if index == 0:
            self.inicio_dedit.setEnabled(False)
            self.final_dedit.setEnabled(False)
        else:
            self.inicio_dedit.setEnabled(True)
            self.final_dedit.setEnabled(True)
            
        if index == 2:
            self.sustitutos_view.setEnabled(False)
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.sustitutos_view.setEnabled(True)
            if not self.sel_model.hasSelection():
                self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        
    def buttonBox_OK(self):
        inicio = self.inicio_dedit.date()
        final = self.final_dedit.date()
        if self.sel_model.hasSelection():
            celdas = self.sel_model.selectedRows(0)#sustituto_id
            pringao = trabajador.Trabajador(None,
                                            celdas[0].data())

        ##Modo simple            
        if self.modo_cbox.currentIndex() == 0:
            self.sustitucion.setSustituto(pringao)
        ##Modo multimple
        elif self.modo_cbox.currentIndex() == 1:
            mis_sustituciones = bajas.Sustituciones()
            cal = calendario.Calendario()            
            for sust in mis_sustituciones.iterable(self.sustitucion.baja()):
                if (inicio <= sust.fecha() <= final and
                    pringao in sust.sustitutos() and
                    cal.getJornada(pringao, sust.fecha()) is personal.Jornada.Ret:
                    sust.setSustituto(pringao)
        ##Modo auto
        elif self.modo_cbox.currentIndex() == 2:
            mis_sustituciones = bajas.Sustituciones()
            for sust in mis_sustituciones.iterable(self.sustitucion.baja()):
                if inicio <= sust.fecha() <= final:
                    candidato = sust.orderedSustitutos()[0]
                    sust.setSustituto(candidato)
        self.accept()        
        
    def seleccionCambiada(self, selected, deselected):
        if selected.isEmpty():
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
            
#######################################################################################
##if __name__ == '__main__':
##    app = QtWidgets.QApplication([])
##    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
##    db.setDatabaseName('operacion.db')
##    if not db.open():
##        import sys
##        sys.exit(1)
##
##     
##    dlg = AsignarDialog(5)
##    dlg.show()
##    app.exec_()
    
