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
            painter.save()
            if necesidades > asignadas:                
                if date == self.selectedDate():
                    color = QtGui.QColor('darkRed')
                else:
                    color = QtGui.QColor('red')
            else:
                if date == self.selectedDate():
                    color = QtGui.QColor('darkGreen')
                else:
                    color = QtGui.QColor('green')
            blanco = QtGui.QColor('white')
            painter.fillRect(rect, QtGui.QBrush(color))
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
