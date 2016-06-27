#!/usr/bin/python3
import sys
import csv

from PyQt5 import QtSql, QtWidgets, QtCore, QtGui

from personal import bajas, trabajador
import anadir_dialog
import asignar_dialog
import baja_dialog
import dbpersonal_dialog
import connection

from ui.mainwindow_ui import Ui_MainWindow

class SustQSqlQueryModel(QtSql.QSqlQueryModel):
    def __init__(self, parent=None, *args):
        super().__init__(parent)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return super().columnCount(parent) + 1
        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.column() == 2:##Sustituido
            if role == QtCore.Qt.DisplayRole:
                sustituido_id = super().data(index, role)
                if sustituido_id == "":
                    return QtCore.QVariant()
                else:
                    return str(trabajador.Trabajador(None, sustituido_id))
        elif index.column() == 7:##Sustituto
            if role == QtCore.Qt.DisplayRole:
                sustituto_id = super().data(index, role)
                if sustituto_id == "":
                    return QtCore.QVariant()
                else:
                    return str(trabajador.Trabajador(None, sustituto_id))
        elif index.column() == 9:##Estado
            asignado = index.sibling(index.row(), 7)##Sustituto
            if asignado.data() == QtCore.QVariant():
                icono = QtGui.QPixmap("./iconos/circulo-rojo.png")
            else:
                icono = QtGui.QPixmap("./iconos/circulo-verde.png")
            pixmap = icono.scaled(QtCore.QSize(25, 25),
                                  QtCore.Qt.KeepAspectRatio,
                                  QtCore.Qt.SmoothTransformation)
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant()
            elif role == QtCore.Qt.DecorationRole:
                return pixmap
            elif role == QtCore.Qt.SizeHintRole:
                return pixmap.size()
            
        if (role == QtCore.Qt.TextAlignmentRole):
            return QtCore.Qt.AlignCenter
        else:
            return super().data(index, role)

class BajasQSqlQueryModel(QtSql.QSqlQueryModel):
    def __init__(self, parent=None, *args):
        super().__init__(parent)
        self.mis_sustituciones = bajas.Sustituciones()

    def columnCount(self, parent=QtCore.QModelIndex()):
        return super().columnCount(parent) + 1
        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.column() == 10:##Estado
            baja = bajas.Baja(None, index.sibling(index.row(), 0).data())
            sustituciones = self.mis_sustituciones.iterable(baja)
            necesidades = len(sustituciones)
            asignadas = 0
        
            for sustitucion in sustituciones:
                if sustitucion.sustituto() is not None:
                    asignadas += 1
                    
            if necesidades > asignadas:
                icono = QtGui.QPixmap("./iconos/circulo-rojo.png")
            else:
                icono = QtGui.QPixmap("./iconos/circulo-verde.png")
            pixmap = icono.scaled(QtCore.QSize(25, 25),
                                  QtCore.Qt.KeepAspectRatio)
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant()
            elif role == QtCore.Qt.DecorationRole:
                return pixmap
            elif role == QtCore.Qt.SizeHintRole:
                return pixmap.size()

        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter
        else:
            return super().data(index, role)

class Gestion(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)

        ####Configuracion de necesidades_view
        self.model = SustQSqlQueryModel(self)
        self.populate_model()
        self.proxy_model = QtCore.QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)        
        hoy = self.calendarWidget.selectedDate().toString(QtCore.Qt.ISODate)
        filtro = QtCore.QRegExp(hoy,
                                QtCore.Qt.CaseInsensitive,
                                QtCore.QRegExp.RegExp)
        self.proxy_model.setFilterKeyColumn(1)##fecha
        self.proxy_model.setFilterRegExp(filtro)
        ##Por defecto ordeno por trabajador no disponible
        self.proxy_model.sort(2, QtCore.Qt.AscendingOrder)
        self.necesidades_view.setModel(self.proxy_model)
               
        self.necesidades_view.hideColumn(0)##sustitucion_id
        self.necesidades_view.hideColumn(1)##fecha
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Fecha")
        self.model.setHeaderData(2, QtCore.Qt.Horizontal,
                                 "Trabajador no disponible")
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, "Puesto")
        self.model.setHeaderData(4, QtCore.Qt.Horizontal, "Unidad")
        self.model.setHeaderData(5, QtCore.Qt.Horizontal, "Turno")
        self.model.setHeaderData(6, QtCore.Qt.Horizontal, "Motivo")
        self.model.setHeaderData(7, QtCore.Qt.Horizontal, "Sustituto")
        self.necesidades_view.hideColumn(8)##baja_id
        self.model.setHeaderData(9, QtCore.Qt.Horizontal, "")##Estado
        self.necesidades_view.horizontalHeader().setSectionsMovable(True)
        ##Poner estado en primer lugar
        self.necesidades_view.horizontalHeader().moveSection(9, 0)
        self.necesidades_view.resizeColumnsToContents()
        ####
        ####Configuracion de bajas_view
        self.bajas_model = BajasQSqlQueryModel(self)
        self.populate_bajas_model()
        self.proxy_bajas_model = QtCore.QSortFilterProxyModel(self)
        self.proxy_bajas_model.setSourceModel(self.bajas_model)        
        self.bajas_view.setModel(self.proxy_bajas_model)
        self.bajas_sel_model = self.bajas_view.selectionModel()
        
        self.bajas_view.hideColumn(0)##baja_id
        self.bajas_model.setHeaderData(1, QtCore.Qt.Horizontal, "Nombre")
        self.bajas_model.setHeaderData(2, QtCore.Qt.Horizontal,
                                       "Primer Apellido")
        self.bajas_model.setHeaderData(3, QtCore.Qt.Horizontal,
                                       "Segundo Apellido")
        self.bajas_model.setHeaderData(4, QtCore.Qt.Horizontal, "Puesto")
        self.bajas_model.setHeaderData(5, QtCore.Qt.Horizontal, "Unidad")
        self.bajas_model.setHeaderData(6, QtCore.Qt.Horizontal, "Equipo")
        self.bajas_model.setHeaderData(7, QtCore.Qt.Horizontal, "Desde")
        self.bajas_model.setHeaderData(8, QtCore.Qt.Horizontal, "Hasta")
        self.bajas_model.setHeaderData(9, QtCore.Qt.Horizontal, "Motivo")
        self.bajas_model.setHeaderData(10, QtCore.Qt.Horizontal, "")
        self.bajas_view.horizontalHeader().setSectionsMovable(True)
        ##Poner estado en primer lugar
        self.bajas_view.horizontalHeader().moveSection(10, 0)
        self.bajas_view.resizeColumnsToContents()
        ####
        ##Configuracion del filtro
        self.filtro_cbox.addItems(["Nombre", "Primer Apellido",
                                   "Segundo Apellido", "Puesto",
                                   "Unidad", "Equipo"])
        self.proxy_bajas_model.setFilterKeyColumn(1) ##por defecto en nombre
        self.buscar_cbox.hide()
        ####Asignacion de eventos
        self.actionEditar_DB_personal.triggered.connect(self.db_personal)
        self.actionAnadir.triggered.connect(self.anadir_btn_clicked)
        self.actionEliminar.triggered.connect(self.eliminar_btn_clicked)
        self.actionModificar.triggered.connect(self.modificar_btn_clicked)
        self.actionImprimir.triggered.connect(self.imprimir)
        self.actionVista_previa.triggered.connect(self.vista_previa)
        self.actionExportar_base_de_datos.triggered.connect(self.exportar_db_csv)
        self.actionImportar_base_de_datos.triggered.connect(self.importar_db_csv)
        self.calendarWidget.clicked.connect(self.calendarWidget_clicked)
        self.necesidades_view.doubleClicked.connect(self.necesidades_dclicked)
        self.tabWidget.currentChanged.connect(self.tab_changed)
        self.bajas_sel_model.selectionChanged.connect(self.seleccion_baja_cambiada)
        self.filtro_cbox.currentIndexChanged.connect(self.filtro_sel_changed)
        self.buscar_ledit.textEdited.connect(self.filtro_text_edited)
        self.buscar_cbox.currentIndexChanged.connect(self.filtro_cbox_edited)
        ####

    def populate_model(self):
        self.model.setQuery("""
            SELECT sustituciones.sustitucion_id, sustituciones.fecha,
                   sustituciones.sustituido_id, puestos.puesto,
                   unidad.unidad, jornadas.turno, bajas.motivo,
                   sustituciones.sustituto_id, sustituciones.baja_id  
            FROM sustituciones, personal, bajas
                INNER JOIN puestos
                ON puestos.puesto_id=personal.puesto
                INNER JOIN unidad
                ON unidad.unidad_id=personal.unidad
                INNER JOIN jornadas
                ON jornadas.turno_id=sustituciones.turno
            WHERE sustituciones.sustituido_id = personal.personal_id
                  AND sustituciones.baja_id = bajas.baja_id
        """)
        self.necesidades_view.resizeColumnsToContents()

    def populate_bajas_model(self):
        self.bajas_model.setQuery("""
            SELECT bajas.baja_id, personal.nombre, personal.apellido1,
                   personal.apellido2, puestos.puesto, unidad.unidad,
                   grupos.grupo, bajas.inicio, bajas.final, bajas.motivo
            FROM personal, bajas
                INNER JOIN unidad
                ON unidad.unidad_id=personal.unidad
                INNER JOIN puestos
                ON puestos.puesto_id=personal.puesto
                INNER JOIN grupos
                ON grupos.grupo_id=personal.grupo
            WHERE personal.personal_id = bajas.sustituido_id
        """)
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
        #Aplico el filtro. Sumo 1 para eliminar la
        #columna anterior al primer valor de filtrado
        #baja_id
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
            QtWidgets.QMessageBox.information(self,
                                              "No se pudo crear el archivo.",
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
            QtWidgets.QMessageBox.information(self,
                                              "No se pudo abrir el archivo.",
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

    def db_personal(self):
        dlg = dbpersonal_dialog.DbPersonalDialog(self)
        dlg.exec_()

    def calendarWidget_clicked(self, date):
        filtro = QtCore.QRegExp(date.toString(QtCore.Qt.ISODate),
                                QtCore.Qt.CaseInsensitive,
                                QtCore.QRegExp.RegExp)
        self.proxy_model.setFilterRegExp(filtro)
        self.necesidades_view.resizeColumnsToContents()

    def necesidades_dclicked(self, index):
        necesidad_id = index.sibling(index.row(), 0)
        dlg = asignar_dialog.AsignarDialog(necesidad_id.data())
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.populate_model()
            self.populate_bajas_model()
    
    def imprimir(self):
        dlg = baja_dialog.ImprimirBajaDialog(self)
        dlg.exec_()        

    def vista_previa(self):
        dlg = baja_dialog.VistaPreviaBajaDialog(self)
        dlg.exec_()

    def tab_changed(self, tab):
        if tab == 0:
            self.proxy_model.setFilterKeyColumn(1)##fecha
            self.proxy_model.sort(2, QtCore.Qt.AscendingOrder)
            self.necesidades_view.hideColumn(1)##fecha
            self.necesidades_view.showColumn(2)##nombre
            self.necesidades_view.showColumn(3)##puesto
            self.necesidades_view.showColumn(4)##unidad
            self.necesidades_view.showColumn(6)##motivo
            self.calendarWidget_clicked(self.calendarWidget.selectedDate())
        if tab == 1:
            self.proxy_model.setFilterKeyColumn(8)##baja_id
            self.proxy_model.sort(1, QtCore.Qt.AscendingOrder)
            self.necesidades_view.showColumn(1)##fecha
            self.necesidades_view.hideColumn(2)##nombre
            self.necesidades_view.hideColumn(3)##puesto
            self.necesidades_view.hideColumn(4)##unidad
            self.necesidades_view.hideColumn(6)##motivo
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
        
###############################################################################3
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    if not connection.createConnection():        
        sys.exit(1)
    window = Gestion()
    window.show()
    app.exec_()
