from PyQt5 import QtWidgets, QtCore, QtGui

from personal import bajas

class MiCalendario(QtWidgets.QCalendarWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.mis_sustituciones = bajas.Sustituciones()

    def paintCell(self, painter, rect, date):
        necesidades = 0
        asignadas = 0
        for sustitucion in self.mis_sustituciones.iterable():
            if sustitucion.fecha() == date:
                necesidades += 1
                if sustitucion.sustituto() != "":
                    asignadas += 1

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
