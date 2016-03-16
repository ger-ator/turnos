import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *
from connection import *

class MiCalendario(QCalendarWidget):
    def __init__(self,parent=None):
        QCalendarWidget.__init__(self,parent)

    def paintCell(self, painter, rect, date):
        query = QSqlQuery()
        query.prepare("SELECT COUNT(Id), COUNT(Asignado) "
                      "FROM necesidades "
                      "WHERE Fecha = ?")
        query.addBindValue(date)
        query.exec_()
        query.first()
        necesidades = query.value(0)
        asignadas = query.value(1)

        if necesidades == 0 or date == self.selectedDate():
            QCalendarWidget.paintCell(self, painter, rect, date)
        else:
            if necesidades > asignadas:
                painter.save()
                painter.fillRect(rect, QBrush(QColor('red')))
                painter.setPen(QColor('white'))
                painter.drawText(rect, Qt.AlignCenter, str(date.day()))
                painter.restore()
            else:
                painter.save()
                painter.fillRect(rect, QBrush(QColor('green')))
                painter.setPen(QColor('white'))
                painter.drawText(rect, Qt.AlignCenter, str(date.day()))
                painter.restore()        

#######################################################################################
if __name__ == '__main__':
    app = QApplication([])
    if not createConnection():
        sys.exit(1)
    dlg = MiCalendario()
    dlg.show()
    app.exec_()
