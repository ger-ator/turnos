#!/usr/bin/python
# -*- coding: utf-8 -*-
 
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *
from PyQt5.QtPrintSupport import *
from connection import *
from trabajador import *
from baja import *
from baja_ui import Ui_Dialog

class BajaDialog(QDialog, Ui_Dialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)

        ##Configuracion del origen de datos
        self.model = QSqlQueryModel(self)
        self.model.setQuery("SELECT personal.nombre, personal.apellido1, "
                            "personal.apellido2, personal.puesto, personal.unidad, "
                            "bajas.motivo, bajas.inicio, bajas.final, bajas.baja_id "
                            "FROM bajas "
                            "INNER JOIN personal ON bajas.sustituido_id = personal.personal_id")
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.bajas_view.setModel(self.proxy_model)
        self.bajas_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sel_model = self.bajas_view.selectionModel()
        self.encabezado = self.bajas_view.horizontalHeader()
        ####
        ##Configuracion visual de la tabla
        columnas = ['Nombre', 'Primer Apellido',
                    'Segundo Apellido', 'Puesto',
                    'Unidad', 'Motivo', 'Desde',
                    'Hasta']
        for index, item in enumerate(columnas):
            self.model.setHeaderData(index, Qt.Horizontal, item)
            self.filtro_cbox.addItem(item)
        self.bajas_view.hideColumn(8) ##baja_id
        self.bajas_view.resizeColumnsToContents()
        ####
        ##Inhabilito OK en buttonbox
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        ####
        ##Asignacion de eventos
        self.buttonBox.accepted.connect(self.buttonBox_OK)
        self.sel_model.selectionChanged.connect(self.seleccionCambiada)
        self.encabezado.sectionClicked.connect(self.encabezado_clicked)
        self.filtro_cbox.currentIndexChanged.connect(self.proxy_model.setFilterKeyColumn)
        self.buscar_ledit.textEdited.connect(self.filtro_text_edited)
        ####

    def filtro_text_edited(self, texto):
        filtro = QRegExp("^{0}".format(texto),
                         Qt.CaseInsensitive,
                         QRegExp.RegExp)
        self.proxy_model.setFilterRegExp(filtro)

    def getBajasId(self):
        filas_sel = self.sel_model.selectedRows()
        return [fila.sibling(fila.row(), 8).data() for fila in filas_sel]

    def buttonBox_OK(self):
        self.accept()

    def encabezado_clicked(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def seleccionCambiada(self, selected, deselected):
        if selected.isEmpty():
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            
class ImprimirBajaDialog(BajaDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar bajas a imprimir")
        self.mes_dedit = QDateEdit(self)
        self.mes_dedit.setCurrentSection(QDateTimeEdit.MonthSection)
        self.mes_dedit.setCalendarPopup(False)
        self.mes_dedit.setObjectName("mes_dedit")
        self.mes_dedit.setDisplayFormat("MM/yyyy")
        self.gridLayout.addWidget(self.mes_dedit, 3, 1, 1, 1)
        self.mes_dedit.setDate(QDate.currentDate())

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

class VistaPreviaBajaDialog(ImprimirBajaDialog):
    def buttonBox_OK(self):
        dialog = QPrintPreviewDialog()
        dialog.printer().setOrientation(QPrinter.Landscape)
        dialog.paintRequested.connect(self.handlePaintRequest)
        dialog.exec_()
        self.accept()

class EliminarBajaDialog(BajaDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar bajas a eliminar")
        
    def buttonBox_OK(self):
        for baja_id in self.getBajasId():
            self.borrar_baja(baja_id)
        self.accept()

    def borrar_baja(self, bajaid):
        ##ESTO LO DEBERIA METER EN LA CLASE BAJA
        query = QSqlQuery()
        query.prepare("DELETE FROM sustituciones WHERE baja_id = ?")
        query.addBindValue(bajaid)
        query.exec_()
        query.prepare("DELETE FROM bajas WHERE baja_id = ?")
        query.addBindValue(bajaid)
        query.exec_()

class ModificarBajaDialog(BajaDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.bajas_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setWindowTitle("Seleccionar baja a modificar")
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.inicio_dedit = QDateEdit(self)
        self.inicio_dedit.setEnabled(False)
        self.inicio_dedit.setCalendarPopup(True)
        self.inicio_dedit.setObjectName("inicio_dedit")
        self.horizontalLayout.addWidget(self.inicio_dedit)
        self.final_dedit = QDateEdit(self)
        self.final_dedit.setEnabled(False)
        self.final_dedit.setCalendarPopup(True)
        self.final_dedit.setObjectName("final_dedit")
        self.horizontalLayout.addWidget(self.final_dedit)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 1, 1, 1)

    def buttonBox_OK(self):
        self.baja_seleccionada.modificaSustituciones(self.inicio_dedit.date(),
                                                     self.final_dedit.date())
        self.accept()

    def seleccionCambiada(self, selected, deselected):
        if selected.isEmpty():
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
            self.inicio_dedit.setEnabled(False)
            self.final_dedit.setEnabled(False)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            self.inicio_dedit.setEnabled(True)
            self.final_dedit.setEnabled(True)
            self.baja_seleccionada = Baja(self.getBajasId()[0]) ##Solo puedo seleccionar una fila
            self.inicio_dedit.setDate(self.baja_seleccionada.inicio)
            self.final_dedit.setDate(self.baja_seleccionada.final)

    def bajas_clicked(self, index):
        baja_id = index.sibling(index.row(),
                                self.model.fieldIndex("baja_id"))
        self.baja = Baja(baja_id.data())
        self.inicio_dedit.setEnabled(True)
        self.final_dedit.setEnabled(True)
        self.buttonBox.setEnabled(True)
        self.inicio_dedit.setDate(self.baja.inicio)    
        self.final_dedit.setDate(self.baja.final)
    
            
#######################################################################################
if __name__ == '__main__':
    app = QApplication([])
    if not createConnection():
        sys.exit(1)
    dlg = ModificarBajaDialog()
    if dlg.exec_():
        print(dlg.getBajasId())
    app.exec_()
##    if dlg.exec_():
##        print(dlg.getData())
