#!/usr/bin/python
# -*- coding: utf-8 -*-
from enum import Enum
from PyQt5 import QtCore, QtWidgets, QtSql, QtGui

from personal import bajas, trabajador

from ui.personal_ui import Ui_Dialog

class ButtonActionRole(Enum):
    addRow = 1
    delRow = 2

class FlipProxyDelegate(QtSql.QSqlRelationalDelegate):
    def createEditor(self, parent, option, index):
        proxy = index.model()
        base_index = proxy.mapToSource(index)
        return super().createEditor(parent, option, base_index)

    def setEditorData(self, editor, index):
        proxy = index.model()
        base_index = proxy.mapToSource(index)
        return super().setEditorData(editor, base_index)

    def setModelData(self, editor, model, index):
        base_model = model.sourceModel()
        base_index = model.mapToSource(index)
        return super().setModelData(editor, base_model, base_index)

class DbPersonalDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)

        self.filtro_cbox.addItems(['Siglas', 'Nombre', 'Primer Apellido',
                                   'Segundo Apellido', 'Puesto', 'Unidad',
                                   'Equipo'])
        ##Por defecto buscar_cbox esta oculto
        self.buscar_cbox.hide()
        ####
        ##Añadir botones a buttonBox
        addrowbutton = QtWidgets.QPushButton("Añadir Fila")
        addrowbutton.setProperty("ActionRole", ButtonActionRole.addRow)
        self.buttonBox.addButton(addrowbutton, QtWidgets.QDialogButtonBox.ActionRole)
        delrowbutton = QtWidgets.QPushButton("Eliminar Fila")
        delrowbutton.setProperty("ActionRole", ButtonActionRole.delRow)
        self.buttonBox.addButton(delrowbutton, QtWidgets.QDialogButtonBox.ActionRole)
        ####
        ##Configuracion del origen de datos
        self.model = QtSql.QSqlRelationalTableModel(self)
        self.model.setTable("personal")
        self.model.setJoinMode(QtSql.QSqlRelationalTableModel.LeftJoin)
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        self.model.setRelation(5, QtSql.QSqlRelation("puestos",
                                                     "puesto_id",
                                                     "puesto"))
        self.model.setRelation(6, QtSql.QSqlRelation("unidad",
                                                     "unidad_id",
                                                     "unidad"))
        self.model.setRelation(7, QtSql.QSqlRelation("grupos",
                                                     "grupo_id",
                                                     "grupo"))
        self.model.select()
        self.proxy_model = QtCore.QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterKeyColumn(1) ##Inicialmente lo posiciono en siglas
        self.personal_view.setModel(self.proxy_model)
        self.personal_view.setItemDelegate(FlipProxyDelegate(self.personal_view))
        ####
        ####Configuracion visual de la tabla
        self.personal_view.hideColumn(0)
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Siglas")
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, "Nombre")
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, "Primer Apellido")
        self.model.setHeaderData(4, QtCore.Qt.Horizontal, "Segundo Apellido")
        self.model.setHeaderData(5, QtCore.Qt.Horizontal, "Puesto")
        self.model.setHeaderData(6, QtCore.Qt.Horizontal, "Unidad")
        self.model.setHeaderData(7, QtCore.Qt.Horizontal, "Equipo")
        self.personal_view.resizeColumnsToContents()
        ####
        ##Asignacion de eventos
        self.filtro_cbox.currentIndexChanged.connect(self.filtro_sel_changed)
        self.buscar_cbox.currentIndexChanged.connect(self.filtro_cbox_edited)
        self.buscar_ledit.textEdited.connect(self.filtro_text_edited)
        self.buttonBox.clicked.connect(self.buttonbox_clicked)
        ####
        
    def buttonbox_clicked(self, boton):
        stdButton = self.buttonBox.standardButton(boton)

        if stdButton == QtWidgets.QDialogButtonBox.Save:
            self.model.submitAll()
            self.accept()        
        elif stdButton == QtWidgets.QDialogButtonBox.Discard:
            self.model.revertAll()
            self.reject()
        elif stdButton == QtWidgets.QDialogButtonBox.NoButton:
            actionrole = boton.property("ActionRole")
            if actionrole is ButtonActionRole.addRow:
                index = self.personal_view.currentIndex()
                self.proxy_model.insertRow(index.row())
            elif actionrole is ButtonActionRole.delRow:
                index = self.personal_view.currentIndex()
                self.proxy_model.removeRow(index.row())

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
            query.exec_("SELECT unidad FROM unidad "
                        "ORDER BY unidad_id ASC")
            while query.next():
                self.buscar_cbox.addItem(query.value(0))
        elif index == 6:
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
        self.buscar_ledit.clear()
        self.proxy_model.setFilterKeyColumn(index + 1)

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
        
#######################################################################################
if __name__ == '__main__':
    import connection
    app = QtWidgets.QApplication([])
    if not connection.createConnection():
        import sys
        sys.exit(1)
    dlg = DbPersonalDialog()
    dlg.show()
    app.exec_()
