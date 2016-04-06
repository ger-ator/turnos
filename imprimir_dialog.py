#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import os
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *
from PyQt5.QtPrintSupport import *
from connection import *
from trabajador import *

path = os.path.dirname(os.path.abspath(__file__))
ImprimirDlgUI, ImprimirDlgBase = uic.loadUiType(os.path.join(path, 'imprimir.ui'))

class ImprimirDialog(ImprimirDlgBase, ImprimirDlgUI):
    def __init__(self, parent = None):
        ImprimirDlgBase.__init__(self, parent)
        self.setupUi(self)

        self.mes_dedit.setDate(QDate.currentDate())
        
        self.filtro_cbox.addItems(['Siglas', 'Nombre', 'Apellido1',
                                   'Apellido2', 'Equipo', 'Puesto'])

        ##Configuracion del origen de datos
        self.model = QSqlRelationalTableModel(self)
        self.model.setTable("bajas")
        self.model.setJoinMode(QSqlRelationalTableModel.InnerJoin)
        self.model.setRelation(self.model.fieldIndex("sustituido_id"),
                               QSqlRelation("personal",
                                            "personal_id",
                                            "siglas, nombre, apellido1, apellido2, puesto, unidad"))
        self.model.select()
        self.bajas_view.setModel(self.model)
        self.bajas_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sel_model = self.bajas_view.selectionModel()
        ####
        ##Configuracion visual de la tabla
        self.bajas_view.hideColumn(self.model.fieldIndex("baja_id"))
        self.bajas_view.hideColumn(self.model.fieldIndex("siglas"))
        self.model.setHeaderData(self.model.fieldIndex("nombre"),
                                 Qt.Horizontal, "Nombre")
        self.model.setHeaderData(self.model.fieldIndex("apellido1"),
                                 Qt.Horizontal, "Primer Apellido")
        self.model.setHeaderData(self.model.fieldIndex("apellido2"),
                                 Qt.Horizontal, "Segundo Apellido")
        self.model.setHeaderData(self.model.fieldIndex("puesto"),
                                 Qt.Horizontal, "Puesto")
        self.model.setHeaderData(self.model.fieldIndex("unidad"),
                                 Qt.Horizontal, "Unidad")
        self.model.setHeaderData(self.model.fieldIndex("motivo"),
                                 Qt.Horizontal, "Motivo")
        self.model.setHeaderData(self.model.fieldIndex("inicio"),
                                 Qt.Horizontal, "Desde")
        self.model.setHeaderData(self.model.fieldIndex("final"),
                                 Qt.Horizontal, "Hasta")
        self.bajas_view.resizeColumnsToContents()
        ####
        ##Inhabilito OK en buttonbox
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        ####
        ##Asignacion de eventos
        self.buscar_ledit.textEdited.connect(self.buscar_text_edited)
        self.buttonBox.accepted.connect(self.buttonBox_OK)
        self.bajas_view.clicked.connect(self.bajas_clicked)
        ####

    def buscar_text_edited(self):
        self.model.setFilter("{0} = '{1}'".format(self.filtro_cbox.currentText().lower(),
                                                        self.buscar_ledit.text()))
        
    def bajas_clicked(self, index):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

    def getBajasId(self):
        filas_sel = self.sel_model.selectedRows()
        return [fila.sibling(fila.row(), 0).data() for fila in filas_sel]

    def buttonBox_OK(self):
        dialog = QPrintDialog()
        dialog.printer().setOrientation(QPrinter.Landscape)
        if dialog.exec_() == QDialog.Accepted:
            self.handlePaintRequest(dialog.printer())
        self.accept()

    def handlePaintRequest(self, printer):
        year = self.mes_dedit.date().year()
        month = self.mes_dedit.date().month()
        dias_mes = self.mes_dedit.date().daysInMonth()
        documento = QTextDocument()

        for baja_id in self.getBajasId():
            cursor = QTextCursor(documento)

            ##Preparar el encabezado de la tabla con los dias del mes
            tabla_turnos = [["{0:02}".format(i+1) for i in range(dias_mes)]]
            tabla_turnos[0].insert(0, "")

            ##Obtener el ID del sustituido
            query = QSqlQuery()
            query.prepare("SELECT sustituido_id FROM bajas WHERE baja_id = ?")
            query.addBindValue(baja_id)
            query.exec_()
            query.first()
            sustituido_id = query.value(0)

            ##Preparo la fila del sustituido
            sustituido = ["" for _ in range(dias_mes + 1)]
            sustituido[0] = str(Trabajador(sustituido_id))
            query.prepare("SELECT strftime('%d', fecha), turno "
                          "FROM sustituciones "
                          "WHERE baja_id = ? AND strftime('%Y-%m', fecha) = ? ")
            query.addBindValue(baja_id)
            query.addBindValue("{0}-{1:02d}".format(year, month))
            query.exec_()
            while query.next():
                    sustituido[int(query.value(0))] = query.value(1)[0]
            tabla_turnos.append(sustituido)

            ##Obtener IDs de los sustitutos
            sustitutos = []
            query.prepare("SELECT sustituto_id "
                          "FROM sustituciones "
                          "WHERE baja_id = ? AND strftime('%Y-%m', fecha) = ?")
            query.addBindValue(baja_id)
            query.addBindValue("{0}-{1:02d}".format(year, month))
            query.exec_()
            while query.next():
                    if query.value(0) is None:
                            continue
                    elif query.value(0) in sustitutos:
                            continue
                    else:
                            sustitutos.append(query.value(0))
                            
            ##Preparo las filas de los sustitutos
            for sustituto in sustitutos:
                if sustituto == "":
                    continue
                else:
                    fila = ["" for _ in range(dias_mes + 1)]
                    query.prepare("SELECT strftime('%d', fecha), turno "
                                  "FROM sustituciones "
                                  "WHERE baja_id = ? AND strftime('%Y-%m', fecha) = ? "
                                  "AND sustituto_id = ?")
                    query.addBindValue(baja_id)
                    query.addBindValue("{0}-{1:02d}".format(year, month))
                    query.addBindValue(sustituto)
                    query.exec_()
                    fila[0] = str(Trabajador(sustituto))
                    while query.next():
                            fila[int(query.value(0))] = query.value(1)[0]
                    tabla_turnos.append(fila)
            
            tabla = cursor.insertTable( len(tabla_turnos), dias_mes + 1)
            for fila in tabla_turnos:
                    for celda in fila:
                            cursor.insertText(str(celda))
                            cursor.movePosition(QTextCursor.NextCell)
        
        documento.print_(printer)

class VistaPreviaDialog(ImprimirDialog):
    def buttonBox_OK(self):
        dialog = QPrintPreviewDialog()
        dialog.printer().setOrientation(QPrinter.Landscape)
        dialog.paintRequested.connect(self.handlePaintRequest)
        dialog.exec_()
        self.accept()
            
#######################################################################################
if __name__ == '__main__':
    app = QApplication([])
    if not createConnection():
        sys.exit(1)
    dlg = ImprimirDialog()
    if dlg.exec_():
        print(dlg.getBajasId())
    app.exec_()
##    if dlg.exec_():
##        print(dlg.getData())
