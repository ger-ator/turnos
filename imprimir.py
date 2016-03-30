import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *
from PyQt5.QtPrintSupport import *
from connection import *
from trabajador import *

def handlePaintRequest(printer):
        printTable(printer, 1, QDate(2016, 3, 1))

def printTable(printer, baja_id, fecha):
        year = fecha.year()
        month = fecha.month()
        dias_mes = fecha.daysInMonth()
        documento = QTextDocument()
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

#######################################################################################
if __name__ == '__main__':
    app = QApplication([])
    if not createConnection():
        sys.exit(1)
    dialog = QPrintPreviewDialog()
    dialog.paintRequested.connect(handlePaintRequest)
    dialog.show()
    dialog.exec_()
##    if dlg.exec_():
##        print(dlg.getData())
            
