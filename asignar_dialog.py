#!/usr/bin/python
# -*- coding: utf-8 -*-
 
from PyQt5 import QtCore, QtWidgets, QtSql

from personal import bajas, trabajador, personal

from ui.asignar_ui import Ui_Dialog

class AsignarDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, sustitucion_id, parent = None):
        super().__init__(parent)
        self.setupUi(self)
        
        self.sustitucion = bajas.Sustitucion(None, sustitucion_id)
        ####
        ##Configuro origen de datos
        self.model = QtSql.QSqlQueryModel(self)
        self.populate_model()
        self.proxy_model = QtCore.QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.sustitutos_view.setModel(self.proxy_model)
        self.sel_model = self.sustitutos_view.selectionModel()
        ####
        ##Filtrar por IDs de posibles sustitutos
        filtro = "|".join(["^{0}$".format(personal_id)
                           for personal_id in self.sustitucion.sustitutos()])
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
        ##Asignacion de eventos
        self.sel_model.selectionChanged.connect(self.seleccionCambiada)
        self.buttonBox.accepted.connect(self.buttonBox_OK)
        self.sustitutos_view.doubleClicked.connect(self.sustitutos_dclicked)
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
        sustituido = trabajador.Trabajador(None, self.sustitucion.sustituido())
        if sustituido.unidad() is personal.Unidad.U2:
            text_query = text_query + "DESC"            
        query.prepare(text_query)
        query.addBindValue(self.sustitucion.fecha())            
        if not query.exec_():
            print(query.lastError().text())            
        self.model.setQuery(query)
        self.sustitutos_view.resizeColumnsToContents()

    def buttonBox_OK(self):
        self.sustitucion.setSustituto(self.pringao)
        self.accept()        
            
    def sustitutos_dclicked(self, index):
        self.trabajador_id = index.sibling(index.row(), 0)##sustituto_id
        self.buttonBox_OK()
        
    def seleccionCambiada(self, selected, deselected):
        if selected.isEmpty():
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
            indices = selected.indexes()
            candidato_id = indices[0].sibling(indices[0].row(), 0).data()
            self.pringao = trabajador.Trabajador(None, candidato_id)
            
#######################################################################################
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('operacion.db')
    if not db.open():
        import sys
        sys.exit(1)

     
    dlg = AsignarDialog(7)
    dlg.show()
    app.exec_()
##    if dlg.exec_():
##        print(dlg.getData())
