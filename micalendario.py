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
                if sustitucion.sustituto() is not None:
                    asignadas += 1
        if necesidades > 0:            
            if necesidades > asignadas:                
                color = QtGui.QColor('red')
            else:
                color = QtGui.QColor('green')
            lado = min([rect.size().width(), rect.size().height()]) // 2.5
            rectangulo = QtCore.QRectF(rect.topLeft(), QtCore.QSizeF(lado, lado))
            rectangulo.moveBottomRight(rect.bottomRight() - QtCore.QPointF(8, 3))
            ##Paso a flotante
            painter.save()
            painter.setRenderHints(QtGui.QPainter.Antialiasing)
            painter.setBrush(color)
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawEllipse(rectangulo)
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
