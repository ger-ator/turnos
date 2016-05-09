#!/usr/bin/python3
import sys
import csv

from PyQt5 import QtSql, QtWidgets, QtCore, QtGui

from personal import bajas
import anadir_dialog
import asignar_dialog
import baja_dialog
import connection

from ui.mainwindow_ui import Ui_MainWindow

class SustitucionesDelegate(QtWidgets.QStyledItemDelegate):
    ##El argumento columna indica la referencia para colorear rojo o verde
    def __init__(self, columna, parent=None, *args):
        super().__init__(parent, *args)
        self.columna = columna

    def paint(self, painter, option, index):
        self.initStyleOption(option, index)        
        painter.save()
        asignado = index.sibling(index.row(), self.columna)
        if asignado.data() == "":
            if option.state & QtWidgets.QStyle.State_Selected:
                color = QtGui.QColor('darkRed')
            else:
                color = QtGui.QColor('red')
        else:            
            if option.state & QtWidgets.QStyle.State_Selected:
                color = QtGui.QColor('darkGreen')
            else:
                color = QtGui.QColor('green')
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        painter.setBrush(QtGui.QBrush(color))
        painter.drawRect(option.rect)
        painter.setPen(QtGui.QPen(QtCore.Qt.white))
        painter.drawText(option.rect, QtCore.Qt.AlignCenter, str(index.data()))
        painter.restore()

class BajasDelegate(QtWidgets.QStyledItemDelegate):
    ##El argumento columna indica la referencia para colorear rojo o verde
    def __init__(self, parent=None, *args):
        super().__init__(parent, *args)
        self.mis_sustituciones = bajas.Sustituciones()

    def paint(self, painter, option, index):
        baja_id = index.sibling(index.row(), 0).data()
        sustituciones = self.mis_sustituciones.iterable(baja_id)
        necesidades = len(sustituciones)
        asignadas = 0
        
        for sustitucion in sustituciones:
            if sustitucion.sustituto() != "":
                asignadas += 1
                    
        self.initStyleOption(option, index)
        painter.save()        
        if necesidades > asignadas:
            if option.state & QtWidgets.QStyle.State_Selected:
                color = QtGui.QColor('darkRed')
            else:
                color = QtGui.QColor('red')
        else:            
            if option.state & QtWidgets.QStyle.State_Selected:
                color = QtGui.QColor('darkGreen')
            else:
                color = QtGui.QColor('green')
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        painter.setBrush(QtGui.QBrush(color))
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
        self.model.setHeaderData(11, QtCore.Qt.Horizontal, "Nombre")
        self.necesidades_view.hideColumn(11)##nombre sustituto
        self.model.setHeaderData(12, QtCore.Qt.Horizontal, "Primer Apellido")
        self.necesidades_view.hideColumn(12)##apellido1 sustituto
        self.model.setHeaderData(13, QtCore.Qt.Horizontal, "Segundo Apellido")
        self.necesidades_view.hideColumn(13)##apellido2 sustituto        
        sust_item_delegate = SustitucionesDelegate(9)##sustituto_id                            
        self.necesidades_view.setItemDelegate(sust_item_delegate)
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
        baja_item_delegate = BajasDelegate(self)                          
        self.bajas_view.setItemDelegate(baja_item_delegate)
        self.bajas_view.resizeColumnsToContents()
        ####
        ##Configuracion del filtro
        self.filtro_cbox.addItems(["Nombre", "Primer Apellido",
                                   "Segundo Apellido", "Puesto",
                                   "Unidad", "Equipo"])
        self.proxy_bajas_model.setFilterKeyColumn(1) ##por defecto en nombre
        self.buscar_cbox.hide()
        ####Asignacion de eventos               
        self.actionAnadir.triggered.connect(self.anadir_btn_clicked)
        self.actionEliminar.triggered.connect(self.eliminar_btn_clicked)
        self.actionModificar.triggered.connect(self.modificar_btn_clicked)
        self.actionImprimir.triggered.connect(self.imprimir)
        self.actionVista_previa.triggered.connect(self.vista_previa)
        self.actionExportar_base_de_datos.triggered.connect(self.exportar_db_csv)
        self.actionImportar_base_de_datos.triggered.connect(self.importar_db_csv)
        self.calendarWidget.clicked.connect(self.calendarWidget_clicked)
        self.necesidades_view.doubleClicked.connect(self.necesidades_dclicked)
        self.necesidades_view.clicked.connect(self.necesidades_clicked)
        self.tabWidget.currentChanged.connect(self.tab_changed)
        self.bajas_sel_model.selectionChanged.connect(self.seleccion_baja_cambiada)
        self.filtro_cbox.currentIndexChanged.connect(self.filtro_sel_changed)
        self.buscar_ledit.textEdited.connect(self.filtro_text_edited)
        self.buscar_cbox.currentIndexChanged.connect(self.filtro_cbox_edited)
        ####

    def populate_model(self):
        self.model.setQuery("SELECT sustituciones.sustitucion_id, "
                            "sustituciones.fecha, personal.nombre, "
                            "personal.apellido1, personal.apellido2, "
                            "puestos.puesto, unidad.unidad, jornadas.turno, "
                            "bajas.motivo, sustituciones.sustituto_id, "
                            "sustituciones.baja_id, sustitutos_dat.nombre, "
                            "sustitutos_dat.apellido1, sustitutos_dat.apellido2 "
                            "FROM sustituciones, personal, bajas "
                            "INNER JOIN puestos "
                            "ON puestos.puesto_id=personal.puesto "
                            "INNER JOIN unidad "
                            "ON unidad.unidad_id=personal.unidad "
                            "INNER JOIN jornadas "
                            "ON jornadas.turno_id=sustituciones.turno "
                            "LEFT JOIN personal AS sustitutos_dat "
                            "ON sustitutos_dat.personal_id=sustituciones.sustituto_id "
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
            self.proxy_bajas_model.setFilterRegExp("")
        self.proxy_bajas_model.setFilterKeyColumn(index + 1)

    def filtro_text_edited(self, texto):
        filtro = QtCore.QRegExp("^{0}".format(texto),
                                QtCore.Qt.CaseInsensitive,
                                QtCore.QRegExp.RegExp)
        self.proxy_bajas_model.setFilterRegExp(filtro)

    def filtro_cbox_edited(self, index):
        filtro = QtCore.QRegExp("^{0}".format(self.buscar_cbox.currentText()),
                                QtCore.Qt.CaseInsensitive,
                                QtCore.QRegExp.RegExp)
        self.proxy_bajas_model.setFilterRegExp(filtro)

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

    def exportar_db_csv(self):
        csvfile, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar CSV",
                                                           "",
                                                           "Tabla CSV (*.csv);; "
                                                           "All Files (*)")
        if not csvfile:
            return
        try:
            file = open(csvfile, 'w')
        except IOError:
            QtWidgets.QMessageBox.information(self, "No se pudo crear el archivo.",
                                              "Error al abrir: {0}".format(csvfile))
            return
        dbase = QtSql.QSqlDatabase.database()
        csvwriter = csv.writer(file, dialect='excel')
        for tabla in dbase.tables(QtSql.QSql.Tables):
            if tabla == "sqlite_sequence":
                continue
            query = QtSql.QSqlQuery()
            query.exec_("SELECT * FROM {0}".format(tabla))
            csvwriter.writerow(["tabla", tabla])
            while query.next():
                num_field = query.record().count()
                csvwriter.writerow([query.value(i) for i in range(num_field)])
        file.close()

    def importar_db_csv(self):
        csvfile, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Guardar CSV",
                                                           "",
                                                           "Tabla CSV (*.csv);; "
                                                           "All Files (*)")
        if not csvfile:
            return
        try:
            file = open(csvfile, newline='')
        except IOError:
            QtWidgets.QMessageBox.information(self, "No se pudo abrir el archivo.",
                                              "Error al abrir: {0}".format(csvfile))
            return
        dbase = QtSql.QSqlDatabase.database()
        csvreader = csv.reader(file, dialect='excel')
        for fila in csvreader:
            if fila[0] == "tabla":
                num_field = dbase.record(fila[1]).count()
                query_txt = "INSERT INTO {0} VALUES({1})".format(fila[1],
                                                                 ",".join(["?"] * num_field))
                continue
            query = QtSql.QSqlQuery()
            query.prepare(query_txt)
            for i in range(num_field):
                query.addBindValue(fila[i])
            query.exec_()             
        file.close()

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
            self.necesidades_view.showColumn(2)##nombre
            self.necesidades_view.showColumn(3)##apellido1
            self.necesidades_view.showColumn(4)##apellido2
            self.necesidades_view.showColumn(5)##puesto
            self.necesidades_view.showColumn(6)##unidad
            self.necesidades_view.showColumn(8)##motivo
            self.necesidades_view.hideColumn(11)##Nombre sustituto
            self.necesidades_view.hideColumn(12)##Apellido1 sustituto
            self.necesidades_view.hideColumn(13)##Apellido2 sustituto
            self.asignado_ledit.show()
            self.label_2.show()
            self.calendarWidget_clicked(self.calendarWidget.selectedDate())
        if tab == 1:
            self.proxy_model.setFilterKeyColumn(10)##baja_id
            self.necesidades_view.showColumn(1)##fecha
            self.necesidades_view.hideColumn(2)##nombre
            self.necesidades_view.hideColumn(3)##apellido1
            self.necesidades_view.hideColumn(4)##apellido2
            self.necesidades_view.hideColumn(5)##puesto
            self.necesidades_view.hideColumn(6)##unidad
            self.necesidades_view.hideColumn(8)##motivo
            self.necesidades_view.showColumn(11)##Nombre sustituto
            self.necesidades_view.showColumn(12)##Apellido1 sustituto
            self.necesidades_view.showColumn(13)##Apellido2 sustituto
            self.asignado_ledit.hide()
            self.label_2.hide()
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
