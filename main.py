#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *
import anadir_dialog
import asignar_dialog
import eliminar_dialog
import imprimir_dialog
import connection
from trabajador import *

path = os.path.dirname(os.path.abspath(__file__))
GestionUI, GestionBase = uic.loadUiType(os.path.join(path, 'mainwindow.ui'))

class MyDelegate(QStyledItemDelegate):
    ##El argumento columna indica la referencia para colorear rojo o verde
    def __init__(self, columna, parent=None, *args):
        QStyledItemDelegate.__init__(self, parent, *args)
        self.columna = columna

    def paint(self, painter, option, index):
        QStyledItemDelegate.paint(self, painter, option, index)
        painter.save()
        asignado = index.sibling(index.row(), self.columna)
        if asignado.data() == "":
            painter.setPen(QPen(Qt.NoPen))
            painter.setBrush(QBrush(QColor('red')))
            painter.drawRect(option.rect)
            painter.setPen(QPen(Qt.white))
            painter.drawText(option.rect, Qt.AlignCenter, index.data())
        else:
            painter.setPen(QPen(Qt.NoPen))
            painter.setBrush(QBrush(QColor('green')))
            painter.drawRect(option.rect)
            painter.setPen(QPen(Qt.white))
            painter.drawText(option.rect, Qt.AlignCenter, index.data())            
        painter.restore()

class Gestion(GestionBase, GestionUI):

    def __init__(self, parent = None):
        GestionBase.__init__(self, parent)
        self.setupUi(self)

        ####Configuracion del origen de datos
        self.model = QSqlRelationalTableModel(self)
        self.model.setTable("sustituciones")
        self.model.setJoinMode(QSqlRelationalTableModel.InnerJoin)
        self.model.setRelation(self.model.fieldIndex("sustituido_id"),
                               QSqlRelation("personal",
                                            "personal_id",
                                            "nombre, apellido1, apellido2, puesto, unidad"))
        self.model.setRelation(self.model.fieldIndex("baja_id"),
                               QSqlRelation("bajas",
                                            "baja_id",
                                            "motivo"))
        self.model.setFilter("fecha = '{0}'".format(self.calendarWidget.selectedDate().toString(Qt.ISODate)))
        self.model.select()
        self.necesidades_view.setModel(self.model)
        self.necesidades_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        ####
        ####Configuracion visual de la tabla
        self.necesidades_view.hideColumn(self.model.fieldIndex("sustitucion_id"))
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
        self.necesidades_view.hideColumn(self.model.fieldIndex("fecha"))
        self.model.setHeaderData(self.model.fieldIndex("turno"),
                                 Qt.Horizontal, "Turno")
        self.necesidades_view.hideColumn(self.model.fieldIndex("sustituto_id"))
        self.necesidades_view.setItemDelegate(MyDelegate(self.model.fieldIndex("sustituto_id")))
        self.necesidades_view.resizeColumnsToContents()
        ####
        self.asignado_ledit.setReadOnly(True)

        ####Asignacion de eventos               
        self.actionAnadir.triggered.connect(self.anadir_btn_clicked)
        self.actionEliminar.triggered.connect(self.eliminar_btn_clicked)
        self.actionImprimir.triggered.connect(self.imprimir)
        self.actionVista_previa.triggered.connect(self.vista_previa)
        self.calendarWidget.clicked.connect(self.calendarWidget_clicked)
        self.necesidades_view.doubleClicked.connect(self.necesidades_dclicked)
        self.necesidades_view.clicked.connect(self.necesidades_clicked)
        ####

    def eliminar_btn_clicked(self):
        dlg = eliminar_dialog.EliminarDialog(self)
        if dlg.exec_():
            self.model.select()
            self.necesidades_view.resizeColumnsToContents()

    def anadir_btn_clicked(self):
        dlg = anadir_dialog.AnadirDialog(self)
        if dlg.exec_():
            self.model.select()
            self.necesidades_view.resizeColumnsToContents()

    def calendarWidget_clicked(self, date):
        self.model.setFilter("Fecha = '{0}'".format(date.toString(Qt.ISODate)))
        self.model.select()
        self.necesidades_view.resizeColumnsToContents()
        self.asignado_ledit.clear()

    def necesidades_dclicked(self, index):
        necesidad_id = index.sibling(index.row(),0)        
        dlg = asignar_dialog.AsignarDialog(necesidad_id.data())
        if dlg.exec_():
            self.model.select()
            self.necesidades_view.resizeColumnsToContents()

    def necesidades_clicked(self, index):
        necesidad_id = index.sibling(index.row(),
                                     self.model.fieldIndex("sustituto_id"))
        query = QSqlQuery()        
        query.prepare("SELECT nombre, apellido1, apellido2 "
                      "FROM personal "
                      "WHERE personal_id = ?")
        query.addBindValue(necesidad_id.data())
        query.exec_()
        query.first()        
        self.asignado_ledit.setText(" ".join(str(query.value(i)) for i in range(3)))
    
    def imprimir(self):
        dlg = imprimir_dialog.ImprimirDialog(VistaPrevia = False)
        if not dlg.exec_() == QDialog.Accepted:
            print("Error al imprimir.")

    def vista_previa(self):
        dlg = imprimir_dialog.ImprimirDialog(VistaPrevia = True)
        if not dlg.exec_() == QDialog.Accepted:
            print("Error al generar vista previa.")

        
###############################################################################3
if __name__ == '__main__':
    app = QApplication([])
    if not connection.createConnection():
        sys.exit(1)
    window = Gestion()
    window.show()
    app.exec_()
