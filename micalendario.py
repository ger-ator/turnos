from PyQt5 import QtWidgets, QtCore, QtGui

from personal import bajas

class MiCalendario(QtWidgets.QCalendarWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.mis_sustituciones = bajas.Sustituciones()

    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)
        
        necesidades = 0
        asignadas = 0
        for sustitucion in self.mis_sustituciones.iterable():
            if sustitucion.fecha() == date:
                necesidades += 1
                if sustitucion.sustituto() != "":
                    asignadas += 1
        if necesidades > 0:            
            if necesidades > asignadas:                
                color = QtGui.QColor('red')
            else:
                color = QtGui.QColor('green')
            painter.save()
            painter.setRenderHints(QtGui.QPainter.Antialiasing)
            painter.setPen(QtGui.QPen(color,
                                      3,
                                      QtCore.Qt.SolidLine,
                                      QtCore.Qt.RoundCap,
                                      QtCore.Qt.RoundJoin))
            rectangulo = QtCore.QRectF(rect)##Paso a flotante
            radio = min([rectangulo.width(), rectangulo.height()]) / 2 - 2
            painter.drawEllipse(rectangulo.center(), radio, radio)
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
