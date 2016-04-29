#!/usr/bin/python3
import sys
from PyQt5 import QtSql, QtWidgets, QtCore, QtGui

import anadir_dialog
import asignar_dialog
import baja_dialog
import connection

from ui.mainwindow_ui import Ui_MainWindow

class MyDelegate(QtWidgets.QStyledItemDelegate):
    ##El argumento columna indica la referencia para colorear rojo o verde
    def __init__(self, columna, parent=None, *args):
        super().__init__(parent, *args)
        self.columna = columna

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        painter.save()
        asignado = index.sibling(index.row(), self.columna)
        if asignado.data() == "":
            painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            painter.setBrush(QtGui.QBrush(QtCore.Qt.red))
            painter.drawRect(option.rect)
            painter.setPen(QtGui.QPen(QtCore.Qt.white))
            painter.drawText(option.rect, QtCore.Qt.AlignCenter, str(index.data()))
        else:
            painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            painter.setBrush(QtGui.QBrush(QtCore.Qt.darkGreen))
            painter.drawRect(option.rect)
            painter.setPen(QtGui.QPen(QtCore.Qt.white))
            painter.drawText(option.rect, QtCore.Qt.AlignCenter, str(index.data()))
        painter.restore()

class Gestion(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)

        ####Configuracion de necesidades_view
        self.model = QtSql.QSqlQueryModel(self)        
        self.populate_model()
        self.proxy_model = QtCore.QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)        
        hoy = self.calendarWidget.selectedDate().toString(QtCore.Qt.ISODate)
        filtro = QtCore.QRegExp(hoy,
                                QtCore.Qt.CaseInsensitive,
                                QtCore.QRegExp.RegExp)
        self.proxy_model.setFilterKeyColumn(1)##fecha
        self.proxy_model.setFilterRegExp(filtro)
        self.necesidades_view.setModel(self.proxy_model)
        
        self.necesidades_view.hideColumn(0)##sustitucion_id
        self.necesidades_view.hideColumn(1)##fecha
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Fecha")
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, "Nombre")
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, "Primer Apellido")
        self.model.setHeaderData(4, QtCore.Qt.Horizontal, "Segundo Apellido")
        self.model.setHeaderData(5, QtCore.Qt.Horizontal, "Puesto")
        self.model.setHeaderData(6, QtCore.Qt.Horizontal, "Unidad")
        self.model.setHeaderData(7, QtCore.Qt.Horizontal, "Turno")
        self.model.setHeaderData(8, QtCore.Qt.Horizontal, "Motivo")
        self.necesidades_view.hideColumn(9)##sustituto_id
        self.necesidades_view.hideColumn(10)##baja_id
        item_delegate = MyDelegate(9)##sustituto_id                            
        self.necesidades_view.setItemDelegate(item_delegate)
        self.necesidades_view.resizeColumnsToContents()
        ####
        ####Configuracion de bajas_view
        self.bajas_model = QtSql.QSqlQueryModel(self)
        self.populate_bajas_model()
        self.proxy_bajas_model = QtCore.QSortFilterProxyModel(self)
        self.proxy_bajas_model.setSourceModel(self.bajas_model)        
        self.bajas_view.setModel(self.proxy_bajas_model)
        self.bajas_sel_model = self.bajas_view.selectionModel()
        
        self.bajas_view.hideColumn(0)##baja_id
        self.bajas_model.setHeaderData(1, QtCore.Qt.Horizontal, "Nombre")
        self.bajas_model.setHeaderData(2, QtCore.Qt.Horizontal, "Primer Apellido")
        self.bajas_model.setHeaderData(3, QtCore.Qt.Horizontal, "Segundo Apellido")
        self.bajas_model.setHeaderData(4, QtCore.Qt.Horizontal, "Puesto")
        self.bajas_model.setHeaderData(5, QtCore.Qt.Horizontal, "Unidad")
        self.bajas_model.setHeaderData(6, QtCore.Qt.Horizontal, "Equipo")
        self.bajas_model.setHeaderData(7, QtCore.Qt.Horizontal, "Desde")
        self.bajas_model.setHeaderData(8, QtCore.Qt.Horizontal, "Hasta")
        self.bajas_model.setHeaderData(9, QtCore.Qt.Horizontal, "Motivo")
        self.bajas_view.resizeColumnsToContents()
        ####Asignacion de eventos               
        self.actionAnadir.triggered.connect(self.anadir_btn_clicked)
        self.actionEliminar.triggered.connect(self.eliminar_btn_clicked)
        self.actionModificar.triggered.connect(self.modificar_btn_clicked)
        self.actionImprimir.triggered.connect(self.imprimir)
        self.actionVista_previa.triggered.connect(self.vista_previa)
        self.calendarWidget.clicked.connect(self.calendarWidget_clicked)
        self.necesidades_view.doubleClicked.connect(self.necesidades_dclicked)
        self.tabWidget.currentChanged.connect(self.tab_changed)
        self.bajas_sel_model.selectionChanged.connect(self.seleccion_baja_cambiada)
        ####

    def populate_model(self):
        self.model.setQuery("SELECT sustituciones.sustitucion_id, "
                            "sustituciones.fecha, personal.nombre, "
                            "personal.apellido1, personal.apellido2, "
                            "puestos.puesto, unidad.unidad, jornadas.turno, "
                            "bajas.motivo, sustituciones.sustituto_id, "
                            "sustituciones.baja_id "
                            "FROM sustituciones, personal, bajas "
                            "INNER JOIN puestos "
                            "ON puestos.puesto_id=personal.puesto "
                            "INNER JOIN unidad "
                            "ON unidad.unidad_id=personal.unidad "
                            "INNER JOIN jornadas "
                            "ON jornadas.turno_id=sustituciones.turno "
                            "WHERE (sustituciones.sustituido_id = personal.personal_id "
                            "AND sustituciones.baja_id = bajas.baja_id) "
                            "ORDER BY sustituciones.fecha")
        self.necesidades_view.resizeColumnsToContents()

    def populate_bajas_model(self):
        self.bajas_model.setQuery("SELECT bajas.baja_id, personal.nombre, "
                                  "personal.apellido1, personal.apellido2, "
                                  "puestos.puesto, unidad.unidad, grupos.grupo, "
                                  "bajas.inicio, bajas.final, bajas.motivo "
                                  "FROM personal, bajas "                                
                                  "INNER JOIN unidad "
                                  "ON unidad.unidad_id=personal.unidad "
                                  "INNER JOIN puestos "
                                  "ON puestos.puesto_id=personal.puesto "
                                  "INNER JOIN grupos "
                                  "ON grupos.grupo_id=personal.grupo "
                                  "WHERE personal.personal_id = bajas.sustituido_id")
        self.bajas_view.resizeColumnsToContents()

    def eliminar_btn_clicked(self):
        dlg = baja_dialog.EliminarBajaDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.populate_model()
            self.populate_bajas_model()

    def anadir_btn_clicked(self):
        dlg = anadir_dialog.AnadirDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.populate_model()
            self.populate_bajas_model()

    def modificar_btn_clicked(self):
        dlg = baja_dialog.ModificarBajaDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.populate_model()
            self.populate_bajas_model()

    def calendarWidget_clicked(self, date):
        filtro = QtCore.QRegExp(date.toString(QtCore.Qt.ISODate),
                                QtCore.Qt.CaseInsensitive,
                                QtCore.QRegExp.RegExp)
        self.proxy_model.setFilterRegExp(filtro)
        self.necesidades_view.resizeColumnsToContents()
        self.asignado_ledit.clear()

    def necesidades_dclicked(self, index):
        necesidad_id = index.sibling(index.row(),0)        
        dlg = asignar_dialog.AsignarDialog(necesidad_id.data())
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.populate_model()
            self.populate_bajas_model()

    def necesidades_clicked(self, index):
        ##VER COMO HAGO ESTO CON QDataWidgetMapper
        necesidad_id = index.sibling(index.row(), 9)##sustituto_id
        query = QtSql.QSqlQuery()        
        query.prepare("SELECT nombre, apellido1, apellido2 "
                      "FROM personal "
                      "WHERE personal_id = ?")
        query.addBindValue(necesidad_id.data())
        query.exec_()
        query.first()
        if query.isValid():
            texto = " ".join(str(query.value(i)) for i in range(3))
            self.asignado_ledit.setText(texto)
        else:
            self.asignado_ledit.clear()
    
    def imprimir(self):
        dlg = baja_dialog.ImprimirBajaDialog(self)
        dlg.exec_()        

    def vista_previa(self):
        dlg = baja_dialog.VistaPreviaBajaDialog(self)
        dlg.exec_()

    def tab_changed(self, tab):
        if tab == 0:
            self.proxy_model.setFilterKeyColumn(1)##fecha
            self.necesidades_view.hideColumn(1)##fecha
            self.calendarWidget_clicked(self.calendarWidget.selectedDate())
        if tab == 1:
            self.proxy_model.setFilterKeyColumn(10)##baja_id
            self.necesidades_view.showColumn(1)##fecha
            if self.bajas_sel_model.hasSelection():
                self.seleccion_baja_cambiada(self.bajas_sel_model.selection(),
                                             None)
            else:
                self.bajas_view.selectRow(0)            

    def seleccion_baja_cambiada(self, selected, deselected):
        if selected.isEmpty():
            filtro = "^{0}$".format(-1)
        else:
            baja_id = selected.indexes()[0].data()
            filtro = "^{0}$".format(baja_id)
        self.proxy_model.setFilterRegExp(filtro)
        self.necesidades_view.resizeColumnsToContents()
        self.asignado_ledit.clear()
        
###############################################################################3
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    if not connection.createConnection():        
        sys.exit(1)
    window = Gestion()
    window.show()
    app.exec_()
