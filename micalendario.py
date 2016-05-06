from PyQt5 import QtSql, QtWidgets, QtCore, QtGui

class MiCalendario(QtWidgets.QCalendarWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

    def paintCell(self, painter, rect, date):
        query = QtSql.QSqlQuery()
        query.prepare("SELECT COUNT(sustitucion_id), COUNT(sustituto_id) "
                      "FROM sustituciones "
                      "WHERE fecha = ?")
        query.addBindValue(date)
        query.exec_()
        query.first()
        necesidades = query.value(0)
        asignadas = query.value(1)

        if necesidades == 0:
            super().paintCell(painter, rect, date)
        else:
            if necesidades > asignadas:
                painter.save()
                if date == self.selectedDate():
                    rojo = QtGui.QColor('darkRed')
                else:
                    rojo = QtGui.QColor('red')
                blanco = QtGui.QColor('white')
                painter.fillRect(rect, QtGui.QBrush(rojo))
                painter.setPen(blanco)
                painter.drawText(rect, QtCore.Qt.AlignCenter, str(date.day()))
                painter.restore()
            else:
                painter.save()
                if date == self.selectedDate():
                    verde = QtGui.QColor('darkGreen')
                else:
                    verde = QtGui.QColor('green')
                blanco = QtGui.QColor('white')
                painter.fillRect(rect, QtGui.QBrush(verde))
                painter.setPen(blanco)
                painter.drawText(rect, QtCore.Qt.AlignCenter, str(date.day()))
                painter.restore()        

#######################################################################################
##if __name__ == '__main__':
##    import connection
##    app = QtWidgets.QApplication([])
##    if not connection.createConnection():
##        import sys
##        sys.exit(1)
##    dlg = MiCalendario()
##    dlg.show()
##    app.exec_()
