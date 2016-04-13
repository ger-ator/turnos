#!/usr/bin/python3
from PyQt5 import QtSql, QtWidgets, QtCore, QtGui

import anadir_dialog
import asignar_dialog
import baja_dialog
import connection

from mainwindow_ui import Ui_MainWindow

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
            painter.drawText(option.rect, QtCore.Qt.AlignCenter, index.data())
        else:
            painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            painter.setBrush(QtGui.QBrush(QtCore.Qt.darkGreen))
            painter.drawRect(option.rect)
            painter.setPen(QtGui.QPen(QtCore.Qt.white))
            painter.drawText(option.rect, QtCore.Qt.AlignCenter, index.data())            
        painter.restore()

class Gestion(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)

        ####Configuracion del origen de datos
        self.model = QtSql.QSqlQueryModel(self)        
        self.populate_model()
        self.proxy_model = QtCore.QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)        
        hoy = self.calendarWidget.selectedDate().toString(QtCore.Qt.ISODate)
        filtro = QtCore.QRegExp(hoy,
                                QtCore.Qt.CaseInsensitive,
                                QtCore.QRegExp.RegExp)
        self.proxy_model.setFilterKeyColumn(9)
        self.proxy_model.setFilterRegExp(filtro)
        self.necesidades_view.setModel(self.proxy_model)
        self.necesidades_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        ####
        ####Configuracion visual de la tabla
        self.necesidades_view.hideColumn(0)##sustitucion_id
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Nombre")
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, "Primer Apellido")
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, "Segundo Apellido")
        self.model.setHeaderData(4, QtCore.Qt.Horizontal, "Puesto")
        self.model.setHeaderData(5, QtCore.Qt.Horizontal, "Unidad")
        self.model.setHeaderData(6, QtCore.Qt.Horizontal, "Turno")
        self.model.setHeaderData(7, QtCore.Qt.Horizontal, "Motivo")
        self.necesidades_view.hideColumn(8)##sustituto_id
        self.necesidades_view.hideColumn(9)##fecha
        item_delegate = MyDelegate(8)##sustituto_id                            
        self.necesidades_view.setItemDelegate(item_delegate)
        self.necesidades_view.resizeColumnsToContents()
        ####
        ####Asignacion de eventos               
        self.actionAnadir.triggered.connect(self.anadir_btn_clicked)
        self.actionEliminar.triggered.connect(self.eliminar_btn_clicked)
        self.actionModificar.triggered.connect(self.modificar_btn_clicked)
        self.actionImprimir.triggered.connect(self.imprimir)
        self.actionVista_previa.triggered.connect(self.vista_previa)
        self.calendarWidget.clicked.connect(self.calendarWidget_clicked)
        self.necesidades_view.doubleClicked.connect(self.necesidades_dclicked)
        self.necesidades_view.clicked.connect(self.necesidades_clicked)
        ####

    def populate_model(self):
        self.model.setQuery("SELECT sustituciones.sustitucion_id, personal.nombre, "
                            "personal.apellido1, personal.apellido2, personal.puesto, "
                            "personal.unidad, sustituciones.turno, bajas.motivo, "
                            "sustituciones.sustituto_id, sustituciones.fecha "
                            "FROM sustituciones, personal, bajas "
                            "WHERE (sustituciones.sustituido_id = personal.personal_id "
                            "AND sustituciones.baja_id = bajas.baja_id)")
        self.necesidades_view.resizeColumnsToContents()

    def eliminar_btn_clicked(self):
        dlg = baja_dialog.EliminarBajaDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.populate_model()

    def anadir_btn_clicked(self):
        dlg = anadir_dialog.AnadirDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.populate_model()

    def modificar_btn_clicked(self):
        dlg = baja_dialog.ModificarBajaDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.populate_model()

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

    def necesidades_clicked(self, index):
        ##VER COMO HAGO ESTO CON QDataWidgetMapper
        necesidad_id = index.sibling(index.row(), 8)##sustituto_id
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
        
###############################################################################3
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    if not connection.createConnection():
        import sys
        sys.exit(1)
    window = Gestion()
    window.show()
    app.exec_()
