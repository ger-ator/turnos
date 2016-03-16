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
import connection

path = os.path.dirname(os.path.abspath(__file__))
GestionUI, GestionBase = uic.loadUiType(os.path.join(path, 'mainwindow.ui'))

class MyDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, *args):
        QStyledItemDelegate.__init__(self, parent, *args)

    def paint(self, painter, option, index):
        QStyledItemDelegate.paint(self, painter, option, index)
        painter.save()
        asignado = index.sibling(index.row(),1)
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
        
        self.model = QSqlQueryModel(self)
        self.necesidades_view.setModel(self.model)
##        self.coloreafilas = MyDelegate(self)
##        self.necesidades_view.setItemDelegate(self.coloreafilas)
        self.necesidades_view.setItemDelegate(MyDelegate(self))
        self.load_necesidades_model(self.calendarWidget.selectedDate())
        self.asignado_ledit.setReadOnly(True)
                
        self.actionAnadir.triggered.connect(self.anadir_btn_clicked)
        self.actionEliminar.triggered.connect(self.eliminar_btn_clicked)
        self.calendarWidget.clicked.connect(self.calendarWidget_clicked)
        self.necesidades_view.doubleClicked.connect(self.necesidades_dclicked)
        self.necesidades_view.clicked.connect(self.necesidades_clicked)

    def eliminar_btn_clicked(self):
        dlg = eliminar_dialog.EliminarDialog(self)
        if dlg.exec_():
            self.load_necesidades_model(self.calendarWidget.selectedDate())

    def anadir_btn_clicked(self):
        dlg = anadir_dialog.AnadirDialog(self)
        if dlg.exec_():
            self.load_necesidades_model(self.calendarWidget.selectedDate())

    def calendarWidget_clicked(self, date):
        self.load_necesidades_model(date)
        self.asignado_ledit.clear()

    def necesidades_dclicked(self, index):
        necesidad_id = index.sibling(index.row(),0)        
        dlg = asignar_dialog.AsignarDialog(necesidad_id.data())
        if dlg.exec_():
            self.load_necesidades_model(self.calendarWidget.selectedDate())
            
###HAGO LOAD_NECESIDADES_MODEL PARA REDIBUJAR
###TENGO QUE REPLANTEARME HACER ESTO DE OTRA MANERA
###A VER SI PUEDO USAR UN QSQLTABLEMODEL            
    def load_necesidades_model(self, fecha):
        query = QSqlQuery()
        query.prepare("SELECT necesidades.Id, necesidades.Asignado, personal.Nombre, "
                      "personal.Apellido1, personal.Apellido2, personal.Puesto, "
                      "personal.Unidad, necesidades.Turno, necesidades.Motivo "
                      "FROM necesidades "
                      "LEFT JOIN personal "
                      "ON necesidades.trabajadorid = personal.Id "
                      "WHERE Fecha = ?")
        query.addBindValue(fecha)
        query.exec_()
        self.model.setQuery(query)
        self.necesidades_view.resizeColumnsToContents()
        self.necesidades_view.hideColumn(0) ##Id
        self.necesidades_view.hideColumn(1) ##Asignado
        

    def necesidades_clicked(self, index):
        necesidad_id = index.sibling(index.row(),0)
        query = QSqlQuery()
        
        query.prepare("SELECT personal.Nombre, personal.Apellido1, personal.Apellido2 "
                      "FROM necesidades "
                      "LEFT JOIN personal ON necesidades.Asignado = personal.Id "
                      "WHERE necesidades.Id = ?")
        query.addBindValue(necesidad_id.data())
        query.exec_()
        query.first()        
        self.asignado_ledit.setText(str(query.value(0)) + " " +
                                    str(query.value(1)) + " " +
                                    str(query.value(2)))
        
        
        
        
###############################################################################3
if __name__ == '__main__':
    app = QApplication([])
    if not connection.createConnection():
        sys.exit(1)
    window = Gestion()
    window.show()
    app.exec_()
