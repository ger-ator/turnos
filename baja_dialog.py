#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui, QtSql, QtPrintSupport

from personal import bajas
import cuadrante

from ui.baja_ui import Ui_Dialog

class BajaDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)
        ##Lista de bajas
        self.mis_bajas = bajas.Bajas()
        ####
        ##Configuracion del origen de datos
        self.model = QtSql.QSqlQueryModel(self)
        self.model.setQuery("SELECT personal.nombre, personal.apellido1, "
                            "personal.apellido2, puestos.puesto, "
                            "unidad.unidad, bajas.motivo, bajas.inicio, "
                            "bajas.final, bajas.baja_id "
                            "FROM bajas "
                            "INNER JOIN personal "
                            "ON bajas.sustituido_id = personal.personal_id "
                            "INNER JOIN puestos "
                            "ON puestos.puesto_id=personal.puesto "
                            "INNER JOIN unidad "
                            "ON unidad.unidad_id=personal.unidad ")
        self.proxy_model = QtCore.QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.bajas_view.setModel(self.proxy_model)
        self.sel_model = self.bajas_view.selectionModel()
        ####
        ##Configuracion visual de la tabla
        columnas = ['Nombre', 'Primer Apellido',
                    'Segundo Apellido', 'Puesto',
                    'Unidad', 'Motivo', 'Desde',
                    'Hasta']
        for index, item in enumerate(columnas):
            self.model.setHeaderData(index, QtCore.Qt.Horizontal, item)
            self.filtro_cbox.addItem(item)
        self.bajas_view.hideColumn(8) ##baja_id
        self.bajas_view.resizeColumnsToContents()
        ####
        ##Inhabilito OK en buttonbox
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        ####
        ##Por defecto buscar_cbox esta oculto
        self.buscar_cbox.hide()
        ####
        ##Asignacion de eventos
        self.buttonBox.accepted.connect(self.buttonBox_OK)
        self.sel_model.selectionChanged.connect(self.seleccionCambiada)
        self.filtro_cbox.currentIndexChanged.connect(self.filtro_sel_changed)
        self.buscar_ledit.textEdited.connect(self.filtro_text_edited)
        self.buscar_cbox.currentIndexChanged.connect(self.filtro_cbox_edited)
        ####

    def filtro_sel_changed(self, index):
        if index == 3:
            self.buscar_ledit.hide()
            self.buscar_cbox.clear()
            self.buscar_cbox.show()
            query = QtSql.QSqlQuery()
            query.exec_("SELECT puesto FROM puestos "
                        "ORDER BY puesto_id ASC")
            while query.next():
                self.buscar_cbox.addItem(query.value(0))            
        elif index == 4:
            self.buscar_ledit.hide()
            self.buscar_cbox.clear()
            self.buscar_cbox.show()
            query = QtSql.QSqlQuery()
            query.exec_("SELECT unidad FROM unidad "
                        "ORDER BY unidad_id ASC")
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

    def getBajas(self):
        filas_sel = self.sel_model.selectedRows(8)#baja_id
        return self.mis_bajas.iterable([fila.data()
                                        for fila in filas_sel])

    def buttonBox_OK(self):
        self.accept()

    def seleccionCambiada(self, selected, deselected):
        if selected.isEmpty():
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
            
class ImprimirBajaDialog(BajaDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar bajas a imprimir")
        self.inicio_dedit.setEnabled(False)
        self.final_dedit.setEnabled(False)

    def buttonBox_OK(self):
        dialog = QtPrintSupport.QPrintDialog()
        dialog.printer().setOrientation(QtPrintSupport.QPrinter.Landscape)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.handlePaintRequest(dialog.printer())
        self.accept()

    def handlePaintRequest(self, printer):
        for baja in self.getBajas():
            doc = cuadrante.Cuadrante(baja,
                                      self.inicio_dedit.date(),
                                      self.final_dedit.date()).toTextDoc()
        doc.print_(printer)

    def seleccionCambiada(self, selected, deselected):
        if selected.isEmpty():
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
            self.inicio_dedit.setEnabled(False)
            self.final_dedit.setEnabled(False)
        else:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
            self.inicio_dedit.setEnabled(True)
            self.final_dedit.setEnabled(True)
            baja_seleccionada = self.getBajas().pop() ##Solo puedo seleccionar una fila
            self.inicio_dedit.setDate(baja_seleccionada.inicio())
            self.final_dedit.setDate(baja_seleccionada.final())

class VistaPreviaBajaDialog(ImprimirBajaDialog):
    def buttonBox_OK(self):
        dialog = QtPrintSupport.QPrintPreviewDialog()
        dialog.printer().setOrientation(QtPrintSupport.QPrinter.Landscape)
        dialog.paintRequested.connect(self.handlePaintRequest)
        dialog.exec_()
        self.accept()

class EliminarBajaDialog(BajaDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar bajas a eliminar")
        self.inicio_dedit.hide()
        self.final_dedit.hide()
        
    def buttonBox_OK(self):
        for baja in self.getBajas():
            self.mis_bajas.delete(baja)
        self.accept()

class ModificarBajaDialog(BajaDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.bajas_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setWindowTitle("Seleccionar baja a modificar")
        self.inicio_dedit.setEnabled(False)
        self.final_dedit.setEnabled(False)

    def buttonBox_OK(self):
        for baja in self.getBajas():
            baja.setInicio(self.inicio_dedit.date())
            baja.setFinal(self.final_dedit.date())
        self.accept()

    def seleccionCambiada(self, selected, deselected):
        if selected.isEmpty():
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
            self.inicio_dedit.setEnabled(False)
            self.final_dedit.setEnabled(False)
        else:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
            self.inicio_dedit.setEnabled(True)
            self.final_dedit.setEnabled(True)
            baja_seleccionada = self.getBajas().pop() ##Solo puedo seleccionar una fila
            self.inicio_dedit.setDate(baja_seleccionada.inicio())
            self.final_dedit.setDate(baja_seleccionada.final())    
            
#######################################################################################
##if __name__ == '__main__':
##    import connection
##    app = QtWidgets.QApplication([])
##    if not connection.createConnection():
##        import sys
##        sys.exit(1)
##    dlg = VistaPreviaBajaDialog()
##    dlg.exec_()        

